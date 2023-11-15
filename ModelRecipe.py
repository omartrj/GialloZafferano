class ModelRecipe:
    title = ""
    link = ""
    category = ""
    difficulty = ""
    rating = ""
    tags = []
    ingredients = []
    imageBase64 = ""

    def toDictionary(self):
        recipe = {
            "title": self.title,
            "link": self.link,
            "category": self.category,
            "difficulty": self.difficulty,
            "rating": self.rating,
            "tags": self.tags,
            "ingredients": self.ingredients,
            "imageBase64": self.imageBase64,
        }
        return recipe
