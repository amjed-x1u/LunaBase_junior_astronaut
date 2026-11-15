LEARNING_CARDS = [
    {
        "title": "1. Why does a lunar base need life-support systems?",
        "body": "The Moon has no breathable atmosphere for humans. A crew needs controlled systems for air, water, temperature, and other essentials. This game simplifies those systems into resource bars.",
        "takeaway": "A habitat must continuously support human needs."
    },
    {
        "title": "2. Water recycling",
        "body": "Water is valuable in space because transporting supplies from Earth is difficult. Real life-support research studies ways to recover and clean water from different sources.",
        "takeaway": "Recycling can reduce the amount of water that must be supplied."
    },
    {
        "title": "3. Oxygen",
        "body": "Astronauts need oxygen to breathe. A real habitat monitors atmosphere composition and uses life-support equipment to maintain safe conditions.",
        "takeaway": "Oxygen is a critical resource, not an optional bonus."
    },
    {
        "title": "4. Solar energy and radiation",
        "body": "Solar panels can generate electrical power when sunlight is available. The lunar surface also has radiation hazards, so mission designs need suitable shielding and operational planning.",
        "takeaway": "Energy and crew protection are different challenges."
    },
    {
        "title": "5. Why does stored food spoil?",
        "body": "Food can spoil when storage is too warm or too humid, when irrigation water carries microbes, or when ripening produce releases ethylene gas. Scientists look at data from sensors to find the cause before choosing a fix.",
        "takeaway": "Find the cause in the data first, then choose the fix."
    },
    {
        "title": "6. Simulation versus reality",
        "body": "A simulation is a simplified model. The numbers in LunaBase are chosen to make the game playable. Real mission design requires engineering models, measured data, and safety margins.",
        "takeaway": "Never treat game values as real spacecraft specifications."
    },
    {
        "title": "7. A real space greenhouse in Antarctica (EDEN ISS)",
        "body": "In 2018 a German-led team ran a greenhouse next to Neumayer Station III in Antarctica as a practice run for space. In about 9 months, a 12.5 square meter growing area produced more than 268 kg of fresh vegetables, mostly eaten by the 10-person winter crew. It grew with LED lights and misted roots instead of soil.",
        "takeaway": "Antarctica is a real test site for growing food far from help."
    },
    {
        "title": "8. Fast crops and slow crops",
        "body": "In the EDEN ISS data a radish batch took about 23 days, arugula 24-29 days, and lettuce about 38 days. Cucumbers ran for about 161 days and tomatoes for the whole 286-day season, giving fruit again and again. That is why the LunaBase greenhouse protects its tomatoes and cucumbers and only checks new seedlings for early growth.",
        "takeaway": "Every crop has its own clock, so plan harvests around it."
    },
    {
        "title": "9. The greenhouse shares the base's resources",
        "body": "A greenhouse is not free food. Its lights need energy and its plants need water, while the plants give back food, oxygen, and some water from the humid air. EDEN ISS tracked power and crew time too. In LunaBase the greenhouse uses simplified numbers, but the real yields per crop come from the EDEN ISS paper.",
        "takeaway": "Growing food trades energy and water for fresh food and cleaner air."
    },
    {
        "title": "10. NASA and growing food in space",
        "body": "Space agencies have studied growing plants for a long time. The EDEN ISS paper itself mentions NASA's Biomass Production Chamber as an earlier space-greenhouse experiment on Earth. In 2015, astronauts on the International Space Station ate red romaine lettuce that was grown on board in the Veggie plant garden.",
        "takeaway": "Growing fresh food could help future crews on the Moon and Mars.",
    },
]

QUIZ = [
    {
        "question": "Why is water recycling useful for a lunar habitat?",
        "options": [
            "It makes gravity stronger",
            "It can reduce the amount of water that must be transported",
            "It removes the need for oxygen",
            "It prevents every solar storm",
        ],
        "answer": "It can reduce the amount of water that must be transported",
        "explanation": "Correct: recovering and reusing water can reduce supply needs."
    },
    {
        "question": "What is the main job of radiation shielding?",
        "options": ["Make solar panels brighter", "Help reduce the crew's radiation exposure", "Create oxygen", "Recycle water"],
        "answer": "Help reduce the crew's radiation exposure",
        "explanation": "Correct: shielding helps protect people and equipment from radiation."
    },
    {
        "question": "Why are LunaBase's numbers not real engineering data?",
        "options": ["They are simplified to make a playable model", "They come from a NASA manual", "Real missions have no resources", "Simulations are always exact"],
        "answer": "They are simplified to make a playable model",
        "explanation": "Correct: a simulation is a simplified model, so game values are not real specifications."
    },
    {
        "question": "Which resource is the most urgent to protect first in the game?",
        "options": ["The one with the shortest estimated reserve", "The one with the nicest emoji", "Always food", "None - events fix everything"],
        "answer": "The one with the shortest estimated reserve",
        "explanation": "Correct: planning around the shortest reserve is exactly how the Mission Coach decides."
    },
    {
        "question": "Which EDEN ISS crop gave the most food per square meter per day?",
        "options": ["Cucumber", "Lettuce", "Radish", "Parsley"],
        "answer": "Cucumber",
        "explanation": "Correct: cucumbers produced about 0.32 kg per square meter per day, far more than lettuce (0.04-0.08)."
    },
    {
        "question": "Why can't a 7-day greenhouse mission grow radishes to harvest size?",
        "options": ["A radish batch took about 23 days in the real data", "Radishes cannot grow in LED light", "Radishes need Earth gravity", "Seven days is long enough for all crops"],
        "answer": "A radish batch took about 23 days in the real data",
        "explanation": "Correct: even the fastest EDEN ISS crop needed over three weeks, so a 7-day mission checks early growth only."
    },
    {
        "question": "What happens in LunaBase if base energy gets very low while the greenhouse is running?",
        "options": ["The grow lights dim and the harvest shrinks", "The harvest doubles", "Nothing changes", "The crew gains oxygen"],
        "answer": "The grow lights dim and the harvest shrinks",
        "explanation": "Correct: plants need light, so a power shortage at the base reduces what the greenhouse can deliver."
    },
]
