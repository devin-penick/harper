const { Component } = require('@harperdb/custom-components');

class TableStatsComponent extends Component {
    constructor() {
        super();
        this.name = 'table-stats';
        this.version = '1.0.0';
    }

    async initialize() {
        // Register custom endpoint
        this.registerEndpoint('GET', '/table-stats/:schema/:table', this.getTableStats.bind(this));
    }

    async getTableStats(req, res) {
        try {
            const { schema, table } = req.params;
            
            // Get table data
            const result = await this.hdb.query({
                operation: 'search_by_value',
                schema,
                table,
                search_attribute: '*',
                get_attributes: ['*']
            });

            if (!result || !Array.isArray(result)) {
                throw new Error('Invalid table data');
            }

            // Calculate statistics
            const stats = {
                total_records: result.length,
                numeric_fields: {},
                string_fields: {}
            };

            if (result.length > 0) {
                // Analyze first record to determine field types
                const firstRecord = result[0];
                
                Object.keys(firstRecord).forEach(field => {
                    const value = firstRecord[field];
                    if (typeof value === 'number') {
                        stats.numeric_fields[field] = {
                            min: value,
                            max: value,
                            sum: value,
                            avg: value
                        };
                    } else if (typeof value === 'string') {
                        stats.string_fields[field] = {
                            total_length: value.length,
                            sample_values: [value]
                        };
                    }
                });

                // Process remaining records
                for (let i = 1; i < result.length; i++) {
                    const record = result[i];
                    Object.keys(record).forEach(field => {
                        const value = record[field];
                        if (typeof value === 'number' && stats.numeric_fields[field]) {
                            const fieldStats = stats.numeric_fields[field];
                            fieldStats.min = Math.min(fieldStats.min, value);
                            fieldStats.max = Math.max(fieldStats.max, value);
                            fieldStats.sum += value;
                            fieldStats.avg = fieldStats.sum / (i + 1);
                        } else if (typeof value === 'string' && stats.string_fields[field]) {
                            const fieldStats = stats.string_fields[field];
                            fieldStats.total_length += value.length;
                            if (fieldStats.sample_values.length < 5) {
                                fieldStats.sample_values.push(value);
                            }
                        }
                    });
                }
            }

            res.json({
                success: true,
                stats
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }
}

module.exports = TableStatsComponent; 