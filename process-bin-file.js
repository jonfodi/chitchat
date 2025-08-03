#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Dynamic import for ES module
async function loadDataflashParser() {
    const module = await import('./src/tools/parsers/JsDataflashParser/parser.js');
    return module.default;
}

class BinFileProcessor {
    constructor() {
        this.parser = null;
        this.DataflashParser = null;
    }

    async initialize() {
        // Load the ES module parser
        this.DataflashParser = await loadDataflashParser();
    }

    async processFile(filePath, outputPath) {
        try {
            // Initialize the parser if not already done
            if (!this.DataflashParser) {
                console.log('Loading DataflashParser...');
                await this.initialize();
            }

            // Read the .bin file
            console.log(`Reading .bin file: ${filePath}`);
            const data = fs.readFileSync(filePath);
            
            // Process using DataflashParser with the same settings as the worker
            console.log('Processing .bin file...');
            this.parser = new this.DataflashParser(true);
            
            // Use the exact same message types as specified in the worker
            const messageTypes = ['CMD', 'MSG', 'FILE', 'MODE', 'AHR2', 'ATT', 'GPS', 'POS',
                'XKQ1', 'XKQ', 'NKQ1', 'NKQ2', 'XKQ2', 'PARM', 'MSG', 'STAT', 'EV', 'XKF4', 'FNCE'];
            
            await this.parser.processData(data, messageTypes);
            
            // Extract results
            console.log('Extracting results...');
            const results = this.getParserResults();
            
            // Write results to output file
            console.log(`Writing results to: ${outputPath}`);
            fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
            
            console.log('Processing complete!');
            
        } catch (error) {
            console.error('Error processing file:', error);
            process.exit(1);
        }
    }

    getParserResults() {
        if (!this.parser) {
            return null;
        }

        const results = {
            metadata: this.parser.metadata || {},
            messages: this.parser.messages || this.parser.messages_list || {},
            files: this.parser.files || [],
            availableMessages: this.parser.availableMessages || []
        };

        return results;
    }
}

// Command line interface
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.log('Usage: node process-bin-file.js <input.bin> [output.json]');
        console.log('');
        console.log('Examples:');
        console.log('  node process-bin-file.js flight.bin');
        console.log('  node process-bin-file.js flight.bin results.json');
        process.exit(1);
    }
    
    const inputFile = args[0];
    const outputFile = args[1] || `${path.basename(inputFile, '.bin')}_processed.json`;
    
    // Check if input file exists and is a .bin file
    if (!fs.existsSync(inputFile)) {
        console.error(`Error: Input file does not exist: ${inputFile}`);
        process.exit(1);
    }
    
    if (!inputFile.toLowerCase().endsWith('.bin')) {
        console.error('Error: Input file must be a .bin file');
        process.exit(1);
    }
    
    // Create processor and run
    const processor = new BinFileProcessor();
    try {
        await processor.processFile(inputFile, outputFile);
        console.log('Script completed successfully!');
    } catch (error) {
        console.error('Script failed:', error);
        process.exit(1);
    }
}

// Run the script
if (require.main === module) {
    main();
}