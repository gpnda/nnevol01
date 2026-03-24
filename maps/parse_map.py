from __future__ import annotations

import csv
from pathlib import Path

import pygame


INPUT_FILE = "map05.bmp"
OUTPUT_FILE = "map05.csv"
SAFE_OUTPUT_FILE = "map05.safe.csv"

RED = (255, 0, 0)
BLACK = (0, 0, 0)
SAFE_BLUE = (0, 100, 223)


def convert_pixel(pixel: tuple[int, ...]) -> tuple[int, int]:
	if len(pixel) != 3:
		raise ValueError(f"Expected RGB pixel, got: {pixel}")
	if pixel == RED:
		return 1, 0
	if pixel == BLACK:
		return 0, 0
	if pixel == SAFE_BLUE:
		return 0, 1
	raise ValueError(f"Unsupported pixel color: {pixel}")


def save_csv(path: Path, rows: list[list[int]]) -> None:
	with path.open("w", newline="", encoding="utf-8") as csv_file:
		writer = csv.writer(csv_file, delimiter=";")
		writer.writerows(rows)


def main() -> None:
	base_dir = Path(__file__).resolve().parent
	input_path = base_dir / INPUT_FILE
	output_path = base_dir / OUTPUT_FILE
	safe_output_path = base_dir / SAFE_OUTPUT_FILE

	pygame.init()
	try:
		surface = pygame.image.load(str(input_path))
		width, height = surface.get_size()

		main_rows: list[list[int]] = []
		safe_rows: list[list[int]] = []

		for y in range(height):
			main_row: list[int] = []
			safe_row: list[int] = []
			for x in range(width):
				color = tuple(surface.get_at((x, y))[:3])
				main_value, safe_value = convert_pixel(color)
				main_row.append(main_value)
				safe_row.append(safe_value)
			main_rows.append(main_row)
			safe_rows.append(safe_row)

		save_csv(output_path, main_rows)
		save_csv(safe_output_path, safe_rows)
	finally:
		pygame.quit()


if __name__ == "__main__":
	main()
