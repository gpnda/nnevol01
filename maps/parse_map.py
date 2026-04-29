from __future__ import annotations

import csv
from pathlib import Path

import pygame


INPUT_FILE = "map06.bmp"
OUTPUT_FILE = "map06.csv"

BLACK = (0, 0, 0)
RED = (255, 0, 0)
SAFE_BLUE = (0, 100, 223)


def convert_pixel(pixel: tuple[int, ...]) -> int:
	if len(pixel) != 3:
		raise ValueError(f"Expected RGB pixel, got: {pixel}")
	if pixel == BLACK:
		return 0
	if pixel == RED:
		return 1
	if pixel == SAFE_BLUE:
		return 9
	raise ValueError(f"Unsupported pixel color: {pixel}")


def save_csv(path: Path, rows: list[list[int]]) -> None:
	with path.open("w", newline="", encoding="utf-8") as csv_file:
		writer = csv.writer(csv_file, delimiter=";")
		writer.writerows(rows)


def main() -> None:
	base_dir = Path(__file__).resolve().parent
	input_path = base_dir / INPUT_FILE
	output_path = base_dir / OUTPUT_FILE

	pygame.init()
	try:
		surface = pygame.image.load(str(input_path))
		width, height = surface.get_size()

		rows: list[list[int]] = []

		for y in range(height):
			row: list[int] = []
			for x in range(width):
				color = tuple(surface.get_at((x, y))[:3])
				value = convert_pixel(color)
				row.append(value)
			rows.append(row)

		save_csv(output_path, rows)
	finally:
		pygame.quit()


if __name__ == "__main__":
	main()
