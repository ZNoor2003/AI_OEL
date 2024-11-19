import random
from typing import List, Tuple
import webbrowser
import os

def get_user_input(prompt: str, min_value: int = 1) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value >= min_value:
                return value
            else:
                print(f"Please enter a number greater than or equal to {min_value}.")
        except ValueError:
            print("Please enter a valid number.")

# Get user input for constants
print("Please enter the following information:")
NUM_CLASSES = get_user_input("Number of classes: ")
NUM_TEACHERS = get_user_input("Number of teachers: ")
NUM_SUBJECTS = get_user_input("Number of subjects: ")
NUM_TIMESLOTS = get_user_input("Number of timeslots per day: ")
NUM_DAYS = get_user_input("Number of days in a week: ")

POPULATION_SIZE = 100
GENERATIONS = 100
MUTATION_RATE = 0.1

# Define types
Timetable = List[List[Tuple[int, int]]]  # [day][timeslot] = (subject, teacher)

def generate_random_timetable() -> Timetable:
    timetable = []
    for _ in range(NUM_DAYS):
        day = []
        for _ in range(NUM_TIMESLOTS):
            subject = random.randint(0, NUM_SUBJECTS - 1)
            teacher = random.randint(0, NUM_TEACHERS - 1)
            day.append((subject, teacher))
        timetable.append(day)
    return timetable

def calculate_fitness(timetable: Timetable) -> float:
    conflicts = 0
    
    # Check for teacher conflicts (same teacher teaching different subjects at the same time)
    for day in timetable:
        for timeslot in day:
            teacher = timeslot[1]
            if sum(1 for slot in day if slot[1] == teacher) > 1:
                conflicts += 1
    
    # Check for subject repetition in a day
    for day in timetable:
        subjects = [slot[0] for slot in day]
        if len(subjects) != len(set(subjects)):
            conflicts += 1
    
    return 1 / (conflicts + 1)  # Higher fitness for fewer conflicts

def crossover(parent1: Timetable, parent2: Timetable) -> Timetable:
    child = []
    for day1, day2 in zip(parent1, parent2):
        crossover_point = random.randint(1, len(day1) - 1)
        child.append(day1[:crossover_point] + day2[crossover_point:])
    return child

def mutate(timetable: Timetable) -> Timetable:
    for day in timetable:
        for i in range(len(day)):
            if random.random() < MUTATION_RATE:
                day[i] = (random.randint(0, NUM_SUBJECTS - 1), random.randint(0, NUM_TEACHERS - 1))
    return timetable

def genetic_algorithm() -> Timetable:
    population = [generate_random_timetable() for _ in range(POPULATION_SIZE)]
    
    for generation in range(GENERATIONS):
        population = sorted(population, key=calculate_fitness, reverse=True)
        
        if calculate_fitness(population[0]) == 1.0:
            print(f"Perfect solution found in generation {generation}")
            return population[0]
        
        new_population = population[:2]  # Keep the two best timetables
        
        while len(new_population) < POPULATION_SIZE:
            parent1, parent2 = random.sample(population[:50], 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)
        
        population = new_population
    
    return max(population, key=calculate_fitness)

def generate_html(timetable: Timetable) -> str:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Timetable</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {
                background-color: #f0f4f8;
                background-image: url("data:image/svg+xml,%3Csvg width='52' height='26' viewBox='0 0 52 26' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d1dce5' fill-opacity='0.4'%3E%3Cpath d='M10 10c0-2.21-1.79-4-4-4-3.314 0-6-2.686-6-6h2c0 2.21 1.79 4 4 4 3.314 0 6 2.686 6 6 0 2.21 1.79 4 4 4 3.314 0 6 2.686 6 6 0 2.21 1.79 4 4 4v2c-3.314 0-6-2.686-6-6 0-2.21-1.79-4-4-4-3.314 0-6-2.686-6-6zm25.464-1.95l8.486 8.486-1.414 1.414-8.486-8.486 1.414-1.414z' /%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            }
        </style>
    </head>
    <body class="min-h-screen py-8">
        <div class="container mx-auto px-4">
            <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
                <h1 class="text-4xl font-bold text-center mb-4 text-indigo-700">School Timetable</h1>
                <p class="text-center text-gray-600 mb-8">Generated using a Genetic Algorithm</p>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    """
    
    for day, schedule in zip(days[:NUM_DAYS], timetable):
        html += f"""
        <div class="bg-white rounded-lg shadow-md overflow-hidden border border-indigo-100">
            <h2 class="text-xl font-semibold bg-indigo-600 text-white p-4">{day}</h2>
            <table class="w-full">
                <thead>
                    <tr class="bg-indigo-50">
                        <th class="p-2 text-left text-indigo-700">Timeslot</th>
                        <th class="p-2 text-left text-indigo-700">Subject</th>
                        <th class="p-2 text-left text-indigo-700">Teacher</th>
                    </tr>
                </thead>
                <tbody>
        """
        for timeslot, (subject, teacher) in enumerate(schedule, 1):
            html += f"""
                    <tr class="border-t border-indigo-100 hover:bg-indigo-50 transition-colors duration-150">
                        <td class="p-2 text-indigo-900">{timeslot}</td>
                        <td class="p-2 text-indigo-900">Subject {subject + 1}</td>
                        <td class="p-2 text-indigo-900">Teacher {teacher + 1}</td>
                    </tr>
            """
        html += """
                </tbody>
            </table>
        </div>
        """
    
    html += f"""
            </div>
        </div>
        <div class="mt-8 text-center text-gray-600">
            <p>Number of Classes: {NUM_CLASSES} | Number of Teachers: {NUM_TEACHERS} | Number of Subjects: {NUM_SUBJECTS}</p>
            <p>Timeslots per Day: {NUM_TIMESLOTS} | Days in Week: {NUM_DAYS}</p>
        </div>
    </body>
    </html>
    """
    return html

def save_html(html: str, filename: str = "timetable.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML timetable saved as {filename}")

def print_timetable(timetable: Timetable):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day, schedule in zip(days[:NUM_DAYS], timetable):
        print(f"\n{day}:")
        for timeslot, (subject, teacher) in enumerate(schedule, 1):
            print(f"  Timeslot {timeslot}: Subject {subject + 1}, Teacher {teacher + 1}")

# Run the genetic algorithm
best_timetable = genetic_algorithm()
print("\nBest Timetable Found:")
print_timetable(best_timetable)
print(f"\nFitness: {calculate_fitness(best_timetable)}")

# Generate and save HTML
html_content = generate_html(best_timetable)
save_html(html_content)

# Open the HTML file in the default web browser
webbrowser.open('file://' + os.path.realpath("timetable.html"))

print("\nAn HTML file 'timetable.html' has been generated and opened in your default web browser.")
print("You can find this file in the same directory as this Python script.")