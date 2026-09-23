#!/usr/bin/env python3
"""
LinkedIn Profile QR Code Generator
Generates a customized QR code image for your LinkedIn profile and displays an ASCII preview in the terminal.
"""

import argparse
import os
import sys
import qrcode
from qrcode.constants import ERROR_CORRECT_H


def normalize_linkedin_url(input_val: str) -> str:
    """Normalize input into a full LinkedIn profile URL."""
    val = input_val.strip()
    if not val:
        raise ValueError("URL or username cannot be empty.")
    if val.startswith("http://") or val.startswith("https://"):
        return val
    if "linkedin.com/in/" in val:
        return f"https://{val}" if not val.startswith("http") else val
    # Assume it's a username or handle
    clean_handle = val.lstrip("@").strip()
    return f"https://www.linkedin.com/in/{clean_handle}/"


def generate_qr(
    url: str,
    output_path: str = "linkedin_qr.png",
    fill_color: str = "#0A66C2",  # Official LinkedIn Blue
    back_color: str = "white",
    box_size: int = 10,
    border: int = 4,
    show_terminal: bool = True,
):
    """Generate QR code and save to file."""
    qr = qrcode.QRCode(
        version=None,  # Automatically determine version
        error_correction=ERROR_CORRECT_H,  # High error correction
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
    # Ensure directory exists if path includes directories
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path)

    print(f"\n✅ QR Code successfully generated for: {url}")
    print(f"📁 Saved to: {os.path.abspath(output_path)}")

    if show_terminal:
        print("\n📱 Terminal Preview (scan directly from screen):")
        qr_terminal = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_H,
            box_size=1,
            border=1,
        )
        qr_terminal.add_data(url)
        qr_terminal.make(fit=True)
        qr_terminal.print_ascii(invert=True)


DEFAULT_LINKEDIN_URL = "https://www.linkedin.com/in/keerthi-kumar-r/"


def main():
    parser = argparse.ArgumentParser(
        description="Generate a high-res QR code for your LinkedIn profile."
    )
    parser.add_argument(
        "-u",
        "--url",
        default=DEFAULT_LINKEDIN_URL,
        help=f"LinkedIn profile URL or username (default: '{DEFAULT_LINKEDIN_URL}')",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="linkedin_qr.png",
        help="Output image file path (default: linkedin_qr.png)",
    )
    parser.add_argument(
        "--fill-color",
        default="#0A66C2",
        help="QR code color (default: #0A66C2 - LinkedIn Blue, use 'black' for standard)",
    )
    parser.add_argument(
        "--back-color",
        default="white",
        help="Background color (default: white)",
    )
    parser.add_argument(
        "--box-size",
        type=int,
        default=10,
        help="Pixel size of each box (default: 10)",
    )
    parser.add_argument(
        "--border",
        type=int,
        default=4,
        help="Border box thickness (default: 4)",
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Disable terminal ASCII preview",
    )

    args = parser.parse_args()

    url_input = args.url
    if not url_input:
        try:
            url_input = input(
                "Enter your LinkedIn profile URL or username (e.g. 'keerthikumar'): "
            ).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(0)

    if not url_input:
        print("Error: No URL or username provided.", file=sys.stderr)
        sys.exit(1)

    full_url = normalize_linkedin_url(url_input)
    generate_qr(
        url=full_url,
        output_path=args.output,
        fill_color=args.fill_color,
        back_color=args.back_color,
        box_size=args.box_size,
        border=args.border,
        show_terminal=not args.no_preview,
    )


if __name__ == "__main__":
    main()
