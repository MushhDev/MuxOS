#!/usr/bin/env python3
"""Generate MuxOS gradient wallpapers"""

import cairo
import math
import os

def create_gradient_wallpaper(width, height, colors, filename, style="diagonal"):
    """Create a gradient wallpaper with the given colors"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    
    if style == "diagonal":
        pattern = cairo.LinearGradient(0, 0, width, height)
    elif style == "horizontal":
        pattern = cairo.LinearGradient(0, 0, width, 0)
    elif style == "vertical":
        pattern = cairo.LinearGradient(0, 0, 0, height)
    elif style == "radial":
        pattern = cairo.RadialGradient(width/2, height/2, 0, width/2, height/2, max(width, height)/1.5)
    
    for i, color in enumerate(colors):
        r, g, b = hex_to_rgb(color)
        pattern.add_color_stop_rgb(i / (len(colors) - 1), r, g, b)
    
    ctx.set_source(pattern)
    ctx.rectangle(0, 0, width, height)
    ctx.fill()
    
    # Add subtle noise/texture
    add_noise(ctx, width, height, 0.02)
    
    # Add vignette
    add_vignette(ctx, width, height, 0.3)
    
    surface.write_to_png(filename)
    print(f"Created: {filename}")

def add_noise(ctx, width, height, intensity):
    """Add subtle noise texture"""
    import random
    for _ in range(int(width * height * 0.001)):
        x = random.randint(0, width)
        y = random.randint(0, height)
        alpha = random.random() * intensity
        ctx.set_source_rgba(1, 1, 1, alpha)
        ctx.rectangle(x, y, 1, 1)
        ctx.fill()

def add_vignette(ctx, width, height, intensity):
    """Add vignette effect"""
    pattern = cairo.RadialGradient(width/2, height/2, 0, width/2, height/2, max(width, height)/1.2)
    pattern.add_color_stop_rgba(0, 0, 0, 0, 0)
    pattern.add_color_stop_rgba(0.7, 0, 0, 0, 0)
    pattern.add_color_stop_rgba(1, 0, 0, 0, intensity)
    ctx.set_source(pattern)
    ctx.rectangle(0, 0, width, height)
    ctx.fill()

def hex_to_rgb(hex_color):
    """Convert hex color to RGB (0-1 range)"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def create_mesh_wallpaper(width, height, colors, filename):
    """Create a mesh gradient wallpaper"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    
    # Base gradient
    pattern = cairo.LinearGradient(0, 0, width, height)
    r1, g1, b1 = hex_to_rgb(colors[0])
    r2, g2, b2 = hex_to_rgb(colors[-1])
    pattern.add_color_stop_rgb(0, r1, g1, b1)
    pattern.add_color_stop_rgb(1, r2, g2, b2)
    ctx.set_source(pattern)
    ctx.rectangle(0, 0, width, height)
    ctx.fill()
    
    # Add colored blobs
    import random
    for i, color in enumerate(colors):
        r, g, b = hex_to_rgb(color)
        x = random.randint(int(width * 0.1), int(width * 0.9))
        y = random.randint(int(height * 0.1), int(height * 0.9))
        radius = random.randint(int(min(width, height) * 0.2), int(min(width, height) * 0.5))
        
        pattern = cairo.RadialGradient(x, y, 0, x, y, radius)
        pattern.add_color_stop_rgba(0, r, g, b, 0.6)
        pattern.add_color_stop_rgba(0.5, r, g, b, 0.3)
        pattern.add_color_stop_rgba(1, r, g, b, 0)
        
        ctx.set_source(pattern)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
    
    add_vignette(ctx, width, height, 0.25)
    surface.write_to_png(filename)
    print(f"Created: {filename}")

def main():
    output_dir = "/usr/share/backgrounds"
    os.makedirs(output_dir, exist_ok=True)
    
    resolutions = [
        (1920, 1080),
        (2560, 1440),
        (3840, 2160)
    ]
    
    themes = {
        "velocity": ["#1e1b4b", "#312e81", "#6366f1", "#0f172a"],
        "ocean": ["#0c4a6e", "#0369a1", "#0ea5e9", "#06b6d4"],
        "forest": ["#052e16", "#166534", "#10b981", "#14b8a6"],
        "sunset": ["#431407", "#9a3412", "#f97316", "#ec4899"],
        "midnight": ["#0f172a", "#1e3a5f", "#3b82f6", "#6366f1"],
        "ember": ["#450a0a", "#991b1b", "#ef4444", "#f97316"],
        "grape": ["#2e1065", "#6b21a8", "#a855f7", "#ec4899"],
        "neon": ["#0f172a", "#1e1b4b", "#22d3ee", "#a855f7"]
    }
    
    for res in resolutions:
        w, h = res
        res_name = f"{w}x{h}"
        
        for theme_name, colors in themes.items():
            # Diagonal gradient
            filename = os.path.join(output_dir, f"muxos-{theme_name}-{res_name}.png")
            create_gradient_wallpaper(w, h, colors, filename, "diagonal")
            
            # Mesh gradient (only for default resolution)
            if res == (1920, 1080):
                mesh_filename = os.path.join(output_dir, f"muxos-{theme_name}-mesh.png")
                create_mesh_wallpaper(w, h, colors, mesh_filename)
    
    # Create default symlink
    default = os.path.join(output_dir, "muxos-default.png")
    velocity = os.path.join(output_dir, "muxos-velocity-1920x1080.png")
    if os.path.exists(velocity) and not os.path.exists(default):
        os.symlink(velocity, default)
    
    print("\nWallpaper generation complete!")

if __name__ == "__main__":
    main()
