from PIL import Image

def make_transparent():
    try:
        img = Image.open("clipboard.png").convert("RGBA")
        datas = img.getdata()
        new_data = []

        for item in datas:
            r, g, b, a = item
            # Calculate luminance
            luma = (0.299 * r + 0.587 * g + 0.114 * b)
            
            # Very low luma means background
            if luma < 15:
                # Soften the edges to avoid harsh cutoffs
                alpha = int((luma / 15.0) * 80)
                new_data.append((r, g, b, alpha))
            else:
                # For brighter regions, scale alpha rapidly to 255 to maintain solid glow
                alpha = int(80 + ((luma - 15) / 40.0) * (255 - 80))
                alpha = min(255, max(0, alpha))
                new_data.append((r, g, b, alpha))

        img.putdata(new_data)
        img.save("clipboard_trans.png", "PNG")
        print("Successfully created clipboard_trans.png")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    make_transparent()
