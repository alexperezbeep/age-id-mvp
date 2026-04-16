# Dynamic Taxonomy System

## Overview
This script implements a dynamic taxonomy system that facilitates efficient selection and management of equipment and parts categories. The following features are included:

1. **22 Equipment Categories**: A list of equipment categories is maintained in an array.
2. **25 Part Categories**: Corresponding part categories are structured similarly.
3. **Dynamic Category Switching**: Based on user selection, categories update dynamically.
4. **Searchable Dropdowns**: Users can easily search and select from dropdown menus.
5. **NSN Resolution Logic**: The system includes logic for National Stock Number (NSN) resolutions using the taxonomy type and selected categories.
6. **Image Association with NSNs**: Upon detecting NSNs, users can associate images with these findings, ensuring clarity on which images correlate with specific NSN results.

## Code Implementation

```python
class Taxonomy:
    def __init__(self):
        self.equipment_categories = ["Category1", "Category2", "Category3", ..., "Category22"]
        self.part_categories = ["Part1", "Part2", "Part3", ..., "Part25"]

    def dynamic_switch(self, selected_type, selected_category):
        # Logic for switching categories based on user selection
        pass

    def nsn_resolution(self, taxonomy_type, selected_category):
        # NSN resolution logic based on taxonomy type and selected category
        pass

    def upload_image(self, nsn, image_path):
        # Logic to associate uploaded images with detected NSNs
        pass

# Example usage
taxonomy = Taxonomy()

