import argparse
from PIL import Image

class Steganography:
    BLACK_PIXEL = (0, 0, 0)

    def _int_to_bin(self, rgb):
        """Convert an integer tuple to a binary (string) tuple."""
        r, g, b = rgb
        return f'{r:08b}', f'{g:08b}', f'{b:08b}'

    def _bin_to_int(self, rgb):
        """Convert a binary (string) tuple to an integer tuple."""
        r, g, b = rgb
        return int(r, 2), int(g, 2), int(b, 2)

    def _merge_text(self, rgb, text):
        """Merge text into RGB tuple."""
        r, g, b = self._int_to_bin(rgb)
        text_bin = ''.join([format(ord(char), '08b') for char in text])
        combined_bin = r[:-2] + text_bin[:2], g[:-2] + text_bin[2:4], b[:-2] + text_bin[4:6]
        return self._bin_to_int(combined_bin)

    def _unmerge_text(self, rgb):
        """Unmerge text from RGB tuple."""
        r, g, b = self._int_to_bin(rgb)
        text_bin = r[-2:] + g[-2:] + b[-2:]
        return ''.join(chr(int(text_bin[i:i+8], 2)) for i in range(0, len(text_bin), 8))

    def merge_text(self, image, text):
        """Merge text into image."""
        # Check the size of text vs image
        max_chars = (image.size[0] * image.size[1] * 3) // 8
        if len(text) > max_chars:
            raise ValueError(f'Too much text to hide in the image. Maximum characters: {max_chars}')

        pixel_map = image.load()
        new_image = image.copy()
        width, height = image.size
        text += '\0' * (max_chars - len(text))  # pad text to fill the entire image
        char_index = 0

        for x in range(width):
            for y in range(height):
                if char_index < len(text):
                    new_image.putpixel((x, y), self._merge_text(pixel_map[x, y], text[char_index]))
                    char_index += 1

        return new_image

    def unmerge_text(self, image):
        """Unmerge text from image."""
        pixel_map = image.load()
        width, height = image.size
        extracted_text = ''

        for x in range(width):
            for y in range(height):
                extracted_text += self._unmerge_text(pixel_map[x, y])
                if extracted_text[-1] == '\0':  # end of text marker
                    return extracted_text[:-1]  # remove the padding

        return extracted_text

def main():
    parser = argparse.ArgumentParser(description='Text Steganography')
    subparser = parser.add_subparsers(dest='command')

    merge_text = subparser.add_parser('merge_text')
    merge_text.add_argument('--image', required=True, help='Image path')
    merge_text.add_argument('--text', required=True, help='Text to hide')
    merge_text.add_argument('--output', required=True, help='Output path')

    unmerge_text = subparser.add_parser('unmerge_text')
    unmerge_text.add_argument('--image', required=True, help='Image path')
    unmerge_text.add_argument('--output', required=True, help='Output path')

    args = parser.parse_args()

    steg = Steganography()

    if args.command == 'merge_text':
        image = Image.open(args.image)
        modified_image = steg.merge_text(image, args.text)
        modified_image.save(args.output)
        print(f'Text merged into {args.image} and saved to {args.output}')

    elif args.command == 'unmerge_text':
        image = Image.open(args.image)
        extracted_text = steg.unmerge_text(image)
        with open(args.output, 'w') as file:
            file.write(extracted_text)
        print(f'Extracted text saved to {args.output}')

if __name__ == '__main__':
    main()
