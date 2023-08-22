const fs = require('fs');
const path = require('path');
const pdf2md = require('@opendocsg/pdf2md');

// Parse command-line arguments
const args = process.argv.slice(2);
const sourceArg = args.find(arg => arg.startsWith('--source='));
const targetArg = args.find(arg => arg.startsWith('--target='));

if (!sourceArg) {
    console.error('Please provide a source directory using --source=<path_to_source_directory>');
    process.exit(1);
}

const sourceDir = sourceArg.split('=')[1];
const targetDir = targetArg ? targetArg.split('=')[1] : sourceDir;  // Default to source directory if not provided

function convertPDFsInDirectory(source, target) {
    const files = fs.readdirSync(source);

    files.forEach(file => {
        const sourceFilePath = path.join(source, file);
        const targetFilePath = path.join(target, file);

        if (fs.statSync(sourceFilePath).isDirectory()) {
            // If it's a directory, recursively process it
            if (!fs.existsSync(targetFilePath)) {
                fs.mkdirSync(targetFilePath);
            }
            convertPDFsInDirectory(sourceFilePath, targetFilePath);
        } else if (path.extname(sourceFilePath) === '.pdf') {
            // If it's a PDF, convert it
            const pdfBuffer = fs.readFileSync(sourceFilePath);
            pdf2md(pdfBuffer)
                .then(text => {
                    const outputFile = path.join(target, path.basename(file, '.pdf') + '-pdf2.md');
                    console.log(`Writing to ${outputFile}...`);
                    fs.writeFileSync(outputFile, text);
                })
                .catch(err => {
                    console.error(`Error processing ${sourceFilePath}:`, err);
                });
        }
    });
}

convertPDFsInDirectory(sourceDir, targetDir);
