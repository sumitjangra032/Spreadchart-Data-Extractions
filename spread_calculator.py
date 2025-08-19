import re

class SpreadBackGenerator:
    def __init__(self, spread_str):
        self.original_spread = spread_str
        # Capture sign, base, and year separately
        self.pattern = re.compile(r'([+-]?)\s*(\d+\*\w{3})(\d{2})')
        self.matches = self.pattern.findall(spread_str)

    def generate(self, years_back):
        all_spreads = []

        for i in range(1, years_back + 1):
            spread_parts = []

            for sign, base, year_suffix in self.matches:
                year = int(year_suffix)
                new_year = year - i

                if new_year < 0:
                    continue

                new_term = f"{sign}{base}{new_year:02d}"
                spread_parts.append(new_term)

            # Join while preserving original signs
            spread_str_i = ' '.join(spread_parts).replace('+-', '-')
            all_spreads.append(spread_str_i)

        return all_spreads
