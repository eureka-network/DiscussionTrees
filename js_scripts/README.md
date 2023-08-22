# PDF to Markdown Converter

This tool converts PDF files to Markdown using the `@opendocsg/pdf2md` package.

## Setup

1. Navigate to the `js_scripts` directory:
   ```bash
   cd js_scripts/parserA
   ```
2. Install the required packages:
   ```bash
   npm install
   ```
...

## Usage

To convert all PDFs in a source directory to Markdown:

```bash
npm run convert -- --source=path_to_source_directory [--target=path_to_target_directory]
```
- Replace path_to_source_directory with the path to your source directory containing the PDFs.
- The --target argument is optional. If not provided, the script will save the converted Markdown files in the source directory.