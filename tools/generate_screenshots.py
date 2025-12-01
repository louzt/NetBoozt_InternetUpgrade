"""
NetBoozt Screenshot Generator
Automatically captures GUI screenshots for documentation

Requirements (dev only, gitignored):
    pip install playwright pillow
    playwright install chromium
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

try:
    from playwright.async_api import async_playwright
    from PIL import Image
except ImportError:
    print("❌ Playwright or Pillow not installed")
    print("Install: pip install playwright pillow")
    print("Then: playwright install chromium")
    sys.exit(1)


class ScreenshotGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def capture_gui(self):
        """Capture screenshots of NetBoozt GUI"""
        print("🎬 Iniciando captura de screenshots...")
        
        async with async_playwright() as p:
            # Launch GUI in background
            import subprocess
            gui_process = subprocess.Popen(
                [sys.executable, "windows/run.py"],
                cwd=Path(__file__).parent.parent,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait for GUI to load
            await asyncio.sleep(5)
            
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page(viewport={"width": 1280, "height": 720})
            
            screenshots = []
            
            try:
                # Main window
                print("📸 Capturando ventana principal...")
                await self._capture_window(page, "main_window.png")
                screenshots.append("main_window.png")
                
                # Optimizations tab
                print("📸 Capturando pestaña Optimizaciones...")
                await self._capture_window(page, "optimizations_tab.png")
                screenshots.append("optimizations_tab.png")
                
                # Profiles tab
                print("📸 Capturando pestaña Perfiles...")
                await self._capture_window(page, "profiles_tab.png")
                screenshots.append("profiles_tab.png")
                
                # Status tab
                print("📸 Capturando pestaña Estado...")
                await self._capture_window(page, "status_tab.png")
                screenshots.append("status_tab.png")
                
                print(f"\n✅ {len(screenshots)} screenshots generados en {self.output_dir}")
                
            finally:
                await browser.close()
                gui_process.terminate()
                
            return screenshots
    
    async def _capture_window(self, page, filename: str):
        """Capture a single window screenshot"""
        # Wait for window to be ready
        await asyncio.sleep(2)
        
        # Take screenshot
        screenshot_path = self.output_dir / filename
        await page.screenshot(path=str(screenshot_path), full_page=True)
        
    def create_thumbnail(self, image_path: Path, max_size: tuple = (400, 300)):
        """Create thumbnail version of screenshot"""
        img = Image.open(image_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        thumb_path = self.output_dir / "thumbs" / image_path.name
        thumb_path.parent.mkdir(exist_ok=True)
        img.save(thumb_path, quality=85, optimize=True)
        
        return thumb_path


async def main():
    """Generate all screenshots"""
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "docs" / "assets" / "screenshots"
    
    generator = ScreenshotGenerator(output_dir)
    
    print("🚀 NetBoozt Screenshot Generator")
    print("=" * 60)
    
    # Capture GUI screenshots
    screenshots = await generator.capture_gui()
    
    # Create thumbnails
    print("\n🖼️  Generando thumbnails...")
    for screenshot in screenshots:
        screenshot_path = output_dir / screenshot
        if screenshot_path.exists():
            thumb = generator.create_thumbnail(screenshot_path)
            print(f"  ✓ {thumb.name}")
    
    print("\n✅ Proceso completado!")
    print(f"📁 Screenshots: {output_dir}")
    print(f"📁 Thumbnails: {output_dir / 'thumbs'}")


if __name__ == "__main__":
    asyncio.run(main())
