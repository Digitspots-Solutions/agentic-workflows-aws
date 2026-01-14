"""
Convert LAUTECH Documentation to PDF for AWS AI Competency Submission

This script converts all markdown documentation to submission-ready PDFs.
Requires: pip install markdown weasyprint
"""

import subprocess
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"
OUTPUT_DIR = Path(__file__).parent.parent / "submission"

# Files to convert
FILES_TO_CONVERT = {
    "PRODUCTION.md": "LAUTECH_Architecture_Guide.pdf",
    "RESPONSIBLE_AI.md": "LAUTECH_Responsible_AI.pdf",
    "SELLER_ONE_PAGER.md": "Seller_OnePager.pdf",
    "SELLER_PRESENTATION.md": "Seller_Presentation.pdf",
    "DATA_GUIDE.md": "LAUTECH_Data_Guide.pdf",
    "RDS_SETUP_COMPLETE.md": "LAUTECH_RDS_Setup.pdf",
}


def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "markdown", "weasyprint"], 
                   capture_output=True)


def convert_md_to_pdf(md_path: Path, pdf_path: Path):
    """Convert a markdown file to PDF using pandoc or fallback"""
    print(f"📄 Converting {md_path.name} -> {pdf_path.name}")
    
    # Try pandoc first (best quality)
    try:
        result = subprocess.run(
            ["pandoc", str(md_path), "-o", str(pdf_path), 
             "--pdf-engine=xelatex", "-V", "geometry:margin=1in"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"   ✅ Created {pdf_path.name}")
            return True
    except FileNotFoundError:
        pass
    
    # Fallback: Try with wkhtmltopdf
    try:
        # First convert to HTML
        import markdown
        with open(md_path, 'r') as f:
            md_content = f.read()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #232f3e; border-bottom: 2px solid #ff9900; padding-bottom: 10px; }}
                h2 {{ color: #232f3e; margin-top: 30px; }}
                h3 {{ color: #545b64; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #232f3e; color: white; }}
                code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
                pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                blockquote {{ border-left: 4px solid #ff9900; padding-left: 15px; color: #666; }}
            </style>
        </head>
        <body>
        {markdown.markdown(md_content, extensions=['tables', 'fenced_code'])}
        </body>
        </html>
        """
        
        html_path = pdf_path.with_suffix('.html')
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        # Try wkhtmltopdf
        result = subprocess.run(
            ["wkhtmltopdf", "--quiet", str(html_path), str(pdf_path)],
            capture_output=True
        )
        
        if result.returncode == 0:
            html_path.unlink()  # Clean up HTML
            print(f"   ✅ Created {pdf_path.name}")
            return True
            
    except Exception as e:
        print(f"   ⚠️ Fallback failed: {e}")
    
    # Final fallback: Just keep the HTML for manual conversion
    print(f"   📝 Created HTML version - convert to PDF manually or install pandoc")
    return False


def main():
    print("=" * 60)
    print("LAUTECH Documentation PDF Converter")
    print("AWS AI Competency Submission Materials")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    
    # Convert README.md from root
    root_readme = Path(__file__).parent.parent / "README.md"
    if root_readme.exists():
        convert_md_to_pdf(root_readme, OUTPUT_DIR / "LAUTECH_Overview.pdf")
    
    # Convert docs
    for md_file, pdf_file in FILES_TO_CONVERT.items():
        md_path = DOCS_DIR / md_file
        if md_path.exists():
            convert_md_to_pdf(md_path, OUTPUT_DIR / pdf_file)
        else:
            print(f"   ⚠️ Not found: {md_file}")
    
    print("\n" + "=" * 60)
    print("✅ Conversion Complete!")
    print(f"📁 Files saved to: {OUTPUT_DIR}")
    print("=" * 60)
    
    # List generated files
    print("\nGenerated files:")
    for f in OUTPUT_DIR.iterdir():
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
