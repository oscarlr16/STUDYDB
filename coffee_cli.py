from db import CoffeeDB
import sys
import os
from datetime import datetime

class CoffeeCLI:
    def __init__(self):
        self.db = CoffeeDB()
        self.current_user = None

    def display_menu(self):
        print("\n=== Coffee Recipe Manager ===")
        print("1. Register User")
        print("2. Login (Set Current User)")
        print("3. Create Recipe")
        print("4. View Recipe")
        print("5. Add Review")
        print("6. Exit")
        return input("Select an option: ")

    def register_user(self):
        print("\n=== User Registration ===")
        username = input("Enter username: ")
        email = input("Enter email: ")
        try:
            user_id = self.db.create_user(username, email)
            print(f"User registered successfully! Your ID is: {user_id}")
            return user_id
        except Exception as e:
            print(f"Error registering user: {str(e)}")
            return None

    def login(self):
        print("\n=== User Login ===")
        user_id = input("Enter your user ID: ")
        try:
            self.current_user = int(user_id)
            print(f"Logged in as user {self.current_user}")
        except ValueError:
            print("Invalid user ID")

    def create_recipe(self):
        if not self.current_user:
            print("Please login first!")
            return

        print("\n=== Create New Recipe ===")
        recipe = {
            "name": input("Recipe name: "),
            "temperature": float(input("Temperature (°C): ")),
            "pressure": float(input("Pressure (bars): ")),
            "grind_size": input("Grind size (fine/medium/coarse): "),
            "dose": float(input("Coffee dose (g): ")),
            "yield": float(input("Yield (g): ")),
            "time": float(input("Extraction time (s): ")),
            "difficulty_level": input("Difficulty level (beginner/intermediate/expert): ")
        }

        try:
            recipe_id = self.db.create_recipe(recipe, self.current_user)
            print(f"Recipe created successfully! Recipe ID: {recipe_id}")
        except Exception as e:
            print(f"Error creating recipe: {str(e)}")

    def view_recipe(self):
        print("\n=== View Recipe ===")
        recipe_id = input("Enter recipe ID: ")
        try:
            recipe = self.db.get_recipe(int(recipe_id))
            if recipe:
                print("\nRecipe Details:")
                print(f"Name: {recipe['name']}")
                print(f"Temperature: {recipe['temperature']}°C")
                print(f"Pressure: {recipe['pressure']} bars")
                print(f"Grind Size: {recipe['grind_size']}")
                print(f"Dose: {recipe['dose']}g")
                print(f"Yield: {recipe['yield']}g")
                print(f"Time: {recipe['time']}s")
                
                if recipe['reviews']:
                    print("\nReviews:")
                    for review in recipe['reviews']:
                        print(f"Rating: {review['rating']}/5")
                        if review['comment']:
                            print(f"Comment: {review['comment']}")
                        print(f"Date: {review['created_at']}")
                        print("---")
            else:
                print("Recipe not found")
        except Exception as e:
            print(f"Error retrieving recipe: {str(e)}")

    def add_review(self):
        if not self.current_user:
            print("Please login first!")
            return

        print("\n=== Add Review ===")
        recipe_id = int(input("Enter recipe ID: "))
        rating = int(input("Rating (1-5): "))
        comment = input("Comment (optional): ")

        try:
            review_id = self.db.add_review(recipe_id, self.current_user, rating, comment)
            print(f"Review added successfully! Review ID: {review_id}")
        except Exception as e:
            print(f"Error adding review: {str(e)}")

    def run(self):
        while True:
            choice = self.display_menu()
            
            if choice == "1":
                self.register_user()
            elif choice == "2":
                self.login()
            elif choice == "3":
                self.create_recipe()
            elif choice == "4":
                self.view_recipe()
            elif choice == "5":
                self.add_review()
            elif choice == "6":
                print("Thank you for using Coffee Recipe Manager!")
                sys.exit(0)
            else:
                print("Invalid option, please try again")

if __name__ == "__main__":
    cli = CoffeeCLI()
    cli.run()