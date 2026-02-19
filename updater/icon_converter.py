import os
import sys
from pathlib import Path
from typing import Set, List
import logging
import xml.etree.ElementTree as ET

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from PIL import Image
    import io
except ImportError:
    logger.error("Pillow not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import cairosvg
except ImportError:
    logger.warning("cairosvg not installed. Please run: pip install -r requirements.txt")
    cairosvg = None


class IconConverter:
    """Handle icon conversion operations"""
    
    SIZES = [64, 128, 256, 512, 1024]
    OUTPUT_FORMATS = ['ico', 'png', 'jpg']
    
    def __init__(self):
        self.converted_files: Set[str] = set()
        self.base_path = self._find_icons_folder()
        self.converted_file_path = self._get_converted_file_path()
        self._load_converted_list()
    
    def _find_executable_path(self) -> Path:
        """Get the path of the current executable"""
        if getattr(sys, 'frozen', False):
            # Running as compiled app
            return Path(sys.executable).parent
        else:
            # Running as script
            return Path(__file__).parent
    
    def _find_icons_folder(self) -> Path:
        """Find icons folder in parent, same, or sibling directories"""
        exec_path = self._find_executable_path()
        logger.info(f"Executable path: {exec_path}")
        
        # Search in parent directory
        parent_icons = exec_path.parent / "icons"
        if parent_icons.is_dir():
            logger.info(f"Found icons folder in parent: {parent_icons}")
            return parent_icons
        
        # Search in same directory
        same_icons = exec_path / "icons"
        if same_icons.is_dir():
            logger.info(f"Found icons folder in same directory: {same_icons}")
            return same_icons
        
        # Search in subdirectories
        for item in exec_path.iterdir():
            if item.is_dir() and item.name == "icons":
                logger.info(f"Found icons folder in subdirectory: {item}")
                return item
        
        raise FileNotFoundError("Could not find 'icons' folder")
    
    def _get_converted_file_path(self) -> Path:
        """Get the path to .converted tracking file"""
        # Store in the icons directory
        return self.base_path / ".converted"
    
    def _load_converted_list(self):
        """Load list of already converted files"""
        if self.converted_file_path.exists():
            with open(self.converted_file_path, 'r', encoding='utf-8') as f:
                self.converted_files = set(line.strip() for line in f if line.strip())
            logger.info(f"Loaded {len(self.converted_files)} previously converted files")
        else:
            self.converted_files = set()
            logger.info("No previous conversion history found")
    
    def _save_converted_list(self):
        """Save list of converted files"""
        with open(self.converted_file_path, 'w', encoding='utf-8') as f:
            for filename in sorted(self.converted_files):
                f.write(filename + '\n')
    
    def _svg_to_png(self, svg_path: Path, output_path: Path) -> bool:
        """Convert SVG to PNG"""
        try:
            if cairosvg is None:
                logger.error("cairosvg is required for SVG conversion")
                return False
            
            cairosvg.svg2png(url=str(svg_path), write_to=str(output_path))
            return True
        except Exception as e:
            logger.error(f"Failed to convert {svg_path} to PNG: {e}")
            return False
    
    def _check_svg_size(self, svg_path: Path) -> bool:
        """Check if SVG width and height are 800"""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            width = root.get('width')
            height = root.get('height')
            
            if not width or not height:
                logger.error(f"Missing width or height attribute in {svg_path}")
                return False
            
            # Remove 'px' suffix if present
            width_str = str(width).rstrip('px')
            height_str = str(height).rstrip('px')
            
            try:
                width_val = float(width_str)
                height_val = float(height_str)
                
                if width_val == 800 and height_val == 800:
                    logger.info(f"✓ SVG size check passed: {svg_path.name} is 800x800")
                    return True
                else:
                    logger.error(f"✗ SVG size mismatch: {svg_path.name} is {width_val}x{height_val}, expected 800x800")
                    return False
            except ValueError:
                logger.error(f"Failed to parse width/height values: width={width}, height={height}")
                return False
        except Exception as e:
            logger.error(f"Failed to check SVG size: {e}")
            return False
    
    def _wait_for_user_input(self, folder_name: str):
        """Pause and wait for user input"""
        print(f"\n{'='*60}")
        print(f"⚠ Processing paused for: {folder_name}")
        print(f"{'='*60}")
        try:
            input("按任意键继续... (Press any key to continue...)")
        except (EOFError, KeyboardInterrupt):
            pass
    
    def _delete_converted_files(self, folder_path: Path, base_name: str):
        """Delete all previously converted files (png, jpg, ico)"""
        for format_dir in self.OUTPUT_FORMATS:
            dir_path = folder_path / format_dir
            if dir_path.exists():
                for file in dir_path.glob(f"{base_name}_*.{format_dir if format_dir != 'ico' else 'ico'}"):
                    try:
                        file.unlink()
                        logger.info(f"Deleted: {file}")
                    except Exception as e:
                        logger.error(f"Failed to delete {file}: {e}")
    
    def _create_variants(self, source_path: Path, folder_path: Path, base_name: str) -> bool:
        """Create variants in different sizes and formats"""
        try:
            # First, ensure we have a PNG to work with
            png_temp = folder_path / f"_temp_{base_name}.png"
            
            if source_path.suffix.lower() == '.svg':
                if not self._svg_to_png(source_path, png_temp):
                    return False
            else:
                logger.error(f"Unsupported source format: {source_path}")
                return False
            
            if not png_temp.exists():
                logger.error(f"Failed to create temporary PNG: {png_temp}")
                return False
            
            # Open the PNG and create variants
            with Image.open(png_temp) as img:
                success = True
                
                for size in self.SIZES:
                    # Resize image
                    resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # Save as PNG
                    png_folder = folder_path / "png"
                    png_folder.mkdir(exist_ok=True)
                    png_path = png_folder / f"{base_name}_{size}.png"
                    resized.save(png_path, 'PNG')
                    logger.info(f"Created: {png_path}")
                    
                    # Save as JPG
                    jpg_folder = folder_path / "jpg"
                    jpg_folder.mkdir(exist_ok=True)
                    jpg_path = jpg_folder / f"{base_name}_{size}.jpg"
                    # Convert RGBA to RGB for JPG
                    if resized.mode == 'RGBA':
                        bg = Image.new('RGB', resized.size, (255, 255, 255))
                        bg.paste(resized, mask=resized.split()[3])
                        bg.save(jpg_path, 'JPEG', quality=95)
                    else:
                        resized.save(jpg_path, 'JPEG', quality=95)
                    logger.info(f"Created: {jpg_path}")
                    
                    # Save as ICO
                    ico_folder = folder_path / "ico"
                    ico_folder.mkdir(exist_ok=True)
                    ico_path = ico_folder / f"{base_name}_{size}.ico"
                    resized.save(ico_path, 'ICO')
                    logger.info(f"Created: {ico_path}")
            
            # Clean up temp file
            if png_temp.exists():
                png_temp.unlink()
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to create variants for {source_path}: {e}")
            return False
    
    def _svg_to_xml(self, svg_path: Path) -> bool:
        """Convert SVG to XML (just copy the SVG file as XML)"""
        try:
            xml_path = svg_path.parent / svg_path.stem.replace('.svg', '') / f"{svg_path.stem}.xml"
            xml_path = svg_path.parent / f"{svg_path.stem}.xml"
            
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created XML from SVG: {xml_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to convert SVG to XML: {e}")
            return False
    
    def _xml_to_svg(self, xml_path: Path) -> bool:
        """Convert XML to SVG (just copy the XML file as SVG)"""
        try:
            svg_path = xml_path.parent / f"{xml_path.stem}.svg"
            
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created SVG from XML: {svg_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to convert XML to SVG: {e}")
            return False
    
    def process_icon_folder(self, folder_path: Path) -> bool:
        """Process a single icon folder"""
        folder_name = folder_path.name
        logger.info(f"\nProcessing folder: {folder_name}")
        
        # Check for update marker files
        update_svg_file = None
        update_xml_file = None
        for file in folder_path.glob("*"):
            if file.is_file() and file.suffix.lower() == ".updatesvg":
                update_svg_file = file
            elif file.is_file() and file.suffix.lower() == ".updatexml":
                update_xml_file = file
        
        # If update files exist, only proceed if the icon is already in .converted
        if update_svg_file or update_xml_file:
            if folder_name not in self.converted_files:
                logger.info(f"Skipping {folder_name} (update file found but not in .converted)")
                return True
            
            logger.info(f"Found update files for {folder_name}, regenerating...")
            
            svg_file = None
            xml_file = None
            
            # Find SVG or XML file
            for file in folder_path.iterdir():
                if file.is_file():
                    if file.suffix.lower() == '.svg':
                        svg_file = file
                    elif file.suffix.lower() == '.xml':
                        xml_file = file
            
            # Handle .updatesvg: delete SVG and regenerate everything
            if update_svg_file and svg_file:
                base_name = svg_file.stem
                logger.info(f"Deleting previously converted files for .updatesvg")
                self._delete_converted_files(folder_path, base_name)
                
                # Delete the old SVG
                try:
                    svg_file.unlink()
                    logger.info(f"Deleted: {svg_file}")
                except Exception as e:
                    logger.error(f"Failed to delete {svg_file}: {e}")
                
                # Delete the .updatesvg marker file
                try:
                    update_svg_file.unlink()
                    logger.info(f"Deleted: {update_svg_file}")
                except Exception as e:
                    logger.error(f"Failed to delete {update_svg_file}: {e}")
                
                # If XML exists, use it to regenerate SVG, then regenerate everything
                if xml_file and xml_file.exists():
                    self._xml_to_svg(xml_file)
                    svg_file = xml_file.parent / f"{xml_file.stem}.svg"
                else:
                    logger.warning(f"No XML file found to regenerate SVG for {folder_name}")
                    return False
            
            # Handle .updatexml: delete XML and regenerate everything
            if update_xml_file and xml_file:
                base_name = xml_file.stem
                logger.info(f"Deleting previously converted files for .updatexml")
                self._delete_converted_files(folder_path, base_name)
                
                # Delete the old XML
                try:
                    xml_file.unlink()
                    logger.info(f"Deleted: {xml_file}")
                except Exception as e:
                    logger.error(f"Failed to delete {xml_file}: {e}")
                
                # Delete the .updatexml marker file
                try:
                    update_xml_file.unlink()
                    logger.info(f"Deleted: {update_xml_file}")
                except Exception as e:
                    logger.error(f"Failed to delete {update_xml_file}: {e}")
                
                # If SVG exists, use it to regenerate XML, then regenerate everything
                if svg_file and svg_file.exists():
                    self._svg_to_xml(svg_file)
                    xml_file = svg_file.parent / f"{svg_file.stem}.xml"
                else:
                    logger.warning(f"No SVG file found to regenerate XML for {folder_name}")
                    return False
            
            # Regenerate the converted files
            if svg_file and svg_file.exists():
                # Check SVG size before processing
                if not self._check_svg_size(svg_file):
                    self._wait_for_user_input(folder_name)
                    return False
                
                base_name = svg_file.stem
                success = self._create_variants(svg_file, folder_path, base_name)
                if success:
                    logger.info(f"✓ Successfully regenerated {folder_name}")
                    return True
                else:
                    logger.error(f"Failed to regenerate {folder_name}")
                    return False
        
        # Normal processing (for newly discovered icons)
        if folder_name in self.converted_files:
            logger.info(f"Skipping {folder_name} (already converted)")
            return True
        
        svg_file = None
        xml_file = None
        
        # Find SVG or XML file
        for file in folder_path.iterdir():
            if file.is_file():
                if file.suffix.lower() == '.svg':
                    svg_file = file
                elif file.suffix.lower() == '.xml':
                    xml_file = file
        
        if not svg_file and not xml_file:
            logger.warning(f"No SVG or XML file found in {folder_name}")
            return False
        
        # Ensure we have both SVG and XML
        if svg_file and not xml_file:
            self._svg_to_xml(svg_file)
            xml_file = svg_file.parent / f"{svg_file.stem}.xml"
        elif xml_file and not svg_file:
            self._xml_to_svg(xml_file)
            svg_file = xml_file.parent / f"{xml_file.stem}.svg"
        
        # Process the SVG file
        if svg_file and svg_file.exists():
            # Check SVG size before processing
            if not self._check_svg_size(svg_file):
                self._wait_for_user_input(folder_name)
                return False
            
            base_name = svg_file.stem
            success = self._create_variants(svg_file, folder_path, base_name)
            
            if success:
                self.converted_files.add(folder_name)
                self._save_converted_list()
                logger.info(f"✓ Successfully processed {folder_name}")
                return True
        
        return False
    
    def run(self):
        """Run the conversion process"""
        logger.info("=" * 60)
        logger.info("Icon Converter Started")
        logger.info(f"Icons folder: {self.base_path}")
        logger.info("=" * 60)
        
        if not self.base_path.exists():
            logger.error(f"Icons folder not found: {self.base_path}")
            return False
        
        # Process each icon folder
        icon_folders = [d for d in self.base_path.iterdir() if d.is_dir()]
        
        if not icon_folders:
            logger.warning("No icon folders found")
            return False
        
        successful = 0
        failed = 0
        
        for folder in sorted(icon_folders):
            if self.process_icon_folder(folder):
                successful += 1
            else:
                failed += 1
        
        logger.info("\n" + "=" * 60)
        logger.info(f"Conversion Complete!")
        logger.info(f"Successful: {successful}, Failed: {failed}")
        logger.info("=" * 60)
        
        return failed == 0


def main():
    """Main entry point"""
    try:
        converter = IconConverter()
        success = converter.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
