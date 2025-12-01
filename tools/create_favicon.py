"""
Favicon Generator for NetBoozt
Uses LOUST logo as app icon and favicon
"""

from pathlib import Path
from PIL import Image

def create_favicons_from_logo(logo_path: Path, output_dir: Path):
    """
    Generate all favicon sizes from LOUST logo
    
    Args:
        logo_path: Path to LGOLST_WHITE.png
        output_dir: Output directory for favicons
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load LOUST logo
    logo = Image.open(logo_path).convert("RGBA")
    
    # Favicon sizes for different use cases
    sizes = [
        (16, 16),   # Browser tab
        (32, 32),   # Taskbar
        (48, 48),   # Desktop shortcut
        (64, 64),   # High DPI displays
        (128, 128), # Retina displays
        (256, 256), # Windows tile / macOS
    ]
    
    favicons = []
    
    print("\n🎨 Generating favicons from LOUST logo...")
    
    for size in sizes:
        # Resize logo maintaining aspect ratio
        favicon = logo.copy()
        favicon.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Create square canvas with transparency
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        
        # Center logo on canvas
        offset_x = (size[0] - favicon.width) // 2
        offset_y = (size[1] - favicon.height) // 2
        canvas.paste(favicon, (offset_x, offset_y), favicon)
        
        # Save PNG
        png_path = output_dir / f"favicon-{size[0]}x{size[1]}.png"
        canvas.save(png_path, "PNG", optimize=True)
        favicons.append(png_path)
        print(f"  ✓ {png_path.name}")
    
    # Create multi-resolution .ico file (Windows)
    print("\n💾 Creating .ico file...")
    ico_path = output_dir / "favicon.ico"
    logo_16 = Image.open(output_dir / "favicon-16x16.png")
    logo_32 = Image.open(output_dir / "favicon-32x32.png")
    logo_48 = Image.open(output_dir / "favicon-48x48.png")
    
    logo_16.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=[logo_32, logo_48]
    )
    print(f"  ✓ {ico_path.name}")
    
    # Create app icon (256x256 for Windows/Linux)
    print("\n🚀 Creating app icon...")
    app_icon_path = output_dir / "netboozt_icon.png"
    app_icon = Image.open(output_dir / "favicon-256x256.png")
    app_icon.save(app_icon_path, "PNG", optimize=True)
    print(f"  ✓ {app_icon_path.name}")
    
    return favicons


if __name__ == "__main__":
    print("=" * 60)
    print("🎨 NetBoozt Favicon Generator")
    print("   Using LOUST logo as app icon")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "docs" / "assets" / "logo"
    logo_path = output_dir / "LGOLST_WHITE.png"
    
    # Check if LOUST logo exists
    if not logo_path.exists():
        print(f"\n❌ ERROR: LOUST logo not found at:")
        print(f"   {logo_path}")
        print(f"\nPlease copy LGOLST_WHITE.png to:")
        print(f"   {output_dir}")
        exit(1)
    
    # Generate all favicons
    create_favicons_from_logo(logo_path, output_dir)
    
    print("\n" + "=" * 60)
    print("✅ All favicons generated successfully!")
    print(f"📁 Output: {output_dir}")
    print("=" * 60)
    print("\nUsage in GUI:")
    print("  root.iconbitmap('docs/assets/logo/favicon.ico')")
    print("\nUsage in README:")
    print("  ![Logo](docs/assets/logo/netboozt_icon.png)")
