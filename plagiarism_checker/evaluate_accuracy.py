from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import pearsonr
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from plagiarism_checker.utils import compare_texts

# Define test cases
test_cases = [
    # Exact matches
    ("Deep learning is a subset of machine learning.", "Deep learning is a subset of machine learning."),
    ("Artificial intelligence is evolving rapidly.", "Artificial intelligence is evolving rapidly."),
    ("Quantum mechanics is fascinating.", "Quantum mechanics is fascinating."),
    ("Data science involves extracting insights from data.", "Data science involves extracting insights from data."),
    ("Mathematics is the foundation of many scientific disciplines.", "Mathematics is the foundation of many scientific disciplines."),
    ("The Earth orbits the Sun.", "The Earth orbits the Sun."),
    ("Water boils at 100 degrees Celsius.", "Water boils at 100 degrees Celsius."),
    ("Photosynthesis is how plants make food.", "Photosynthesis is how plants make food."),
    ("Gravity pulls objects toward the Earth.", "Gravity pulls objects toward the Earth."),
    ("The speed of light is approximately 299,792 km/s.", "The speed of light is approximately 299,792 km/s."),
    
    # High similarity
    ("Neural networks are a key component of deep learning.", "Deep learning relies on neural networks."),
    ("Machine learning models are trained with data.", "Data is used to train machine learning algorithms."),
    ("Natural language processing enables computers to understand human speech.", "Computers can understand speech using natural language processing."),
    ("Self-driving cars use AI to navigate roads.", "AI helps autonomous vehicles move safely."),
    ("The sun rises in the east and sets in the west.", "In the east, the sun rises, and in the west, it sets."),
    ("The moon orbits the Earth.", "Earth's satellite, the moon, revolves around it."),
    ("Ecosystems consist of interacting organisms.", "Living beings interact within ecosystems."),
    ("Climate change is affecting global temperatures.", "Rising temperatures are linked to climate change."),
    ("Electricity powers modern civilization.", "Modern civilization depends on electrical energy."),
    ("DNA carries genetic information.", "Genetic information is stored in DNA molecules."),
    
    # Moderate similarity
    ("The weather was hot and sunny.", "It was sunny and warm outside."),
    ("The cat sat on the mat.", "On the mat, the cat was sitting."),
    ("The Eiffel Tower is located in Paris.", "Paris is home to the Eiffel Tower."),
    ("The capital of France is Paris.", "Paris is the capital of France."),
    ("The economy is improving.", "Stock markets are reaching all-time highs."),
    ("Music influences human emotions.", "People’s emotions can be affected by music."),
    ("Exercise improves physical health.", "Physical fitness is enhanced through exercise."),
    ("Renewable energy sources reduce pollution.", "Using renewable energy helps lower pollution levels."),
    ("Bacteria are microscopic organisms.", "Microorganisms include bacteria."),
    ("The ocean covers most of the Earth's surface.", "A large part of the Earth is covered by oceans."),
    
    # Complex paraphrasing
    ("Deep learning uses artificial neural networks to model complex patterns in data.", 
     "Artificial neural networks are used in deep learning to detect intricate patterns in data."),
    ("She baked a cake for the party.", "A cake was baked by her for the party."),
    ("He wrote a letter to his friend.", "A letter was written by him to his friend."),
    ("I went to the store yesterday.", "I am going to the store tomorrow."),
    ("Technology is advancing rapidly.", "The pace of technological progress is accelerating."),
    ("A balanced diet is essential for health.", "Health depends on a well-balanced diet."),
    ("Robots are used in manufacturing industries.", "Manufacturing industries rely on robots for automation."),
    ("Artificial intelligence enhances decision-making.", "AI helps improve the decision-making process."),
    ("Global warming is a serious issue.", "The issue of climate change is highly concerning."),
    ("Computers process data at high speeds.", "Data processing speeds are high in modern computers."),
    
    # Low similarity
    ("Quantum mechanics is fascinating.", "I love eating pizza."),
    ("Artificial intelligence is a field of study in computer science.", "The moon is made of cheese."),
    ("Python is a popular programming language.", "Elephants are the largest land animals."),
    ("The stock market crashed yesterday.", "I enjoy watching movies on weekends."),
    ("Data science requires statistical knowledge.", "Mount Everest is the tallest mountain."),
    ("My favorite color is blue.", "The Great Wall of China is a famous landmark."),
    ("The periodic table organizes chemical elements.", "I like playing soccer with my friends."),
    ("Photosynthesis occurs in plants.", "Chocolate cake is delicious."),
    ("Artificial satellites orbit Earth.", "Ballet is a form of dance."),
    ("The Milky Way is our galaxy.", "A cat has four legs."),
]

# Expected similarity scores (update with actual expected values)
expected_scores = [
    100] * 10 + [90, 85, 88, 80, 75, 87, 83, 81, 86, 82] + [65, 60, 70, 68, 55, 62, 64, 66, 63, 67] + \
    [50, 45, 40, 48, 35, 44, 42, 46, 41, 43] + [10, 5, 7, 8, 6, 4, 3, 2, 1, 0]

assert len(expected_scores) == len(test_cases), "Mismatch in test cases and expected scores"

# Compute predicted similarity scores
predicted_scores = [compare_texts(t1, t2)[0] for t1, t2 in test_cases]

# Compute error metrics
mae = mean_absolute_error(expected_scores, predicted_scores)
mse = mean_squared_error(expected_scores, predicted_scores)

# Compute Pearson correlation safely
try:
    if len(set(predicted_scores)) > 1:
        correlation, _ = pearsonr(expected_scores, predicted_scores)
    else:
        correlation = 0  # No variation in data
except Exception:
    correlation = 0

# Print results
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Pearson Correlation: {correlation:.2f}")
