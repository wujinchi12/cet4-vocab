"""Generate 5 mock CET-4 exam papers (2022-2026) and seed the database."""
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, engine, Base
from app.models.exam import ExamPaper, ExamQuestion
from app.models.word import Word

# ============================================================
# Hand-crafted cloze passages (1 per year, 10 blanks each)
# ============================================================
CLOZE_TEMPLATES = {
    2022: {
        "passage": (
            "In today's digital age, the way people communicate has [BLANK_0] dramatically. "
            "Social media platforms have become an [BLANK_1] part of daily life, connecting "
            "millions of people across the globe. However, this technological [BLANK_2] has "
            "also brought new challenges. Many people find it difficult to [BLANK_3] a balance "
            "between online and offline interactions. Studies show that excessive screen time "
            "can [BLANK_4] to decreased attention spans and reduced face-to-face communication "
            "skills. Experts [BLANK_5] that individuals should set clear boundaries for their "
            "digital consumption. They suggest [BLANK_6] regular breaks from electronic devices "
            "and engaging in more physical activities. Despite these concerns, the benefits of "
            "digital communication cannot be [BLANK_7]. It has made information more [BLANK_8] "
            "than ever before and has created new [BLANK_9] for education and business."
        ),
        "blanks": [
            {"answer": "changed", "options": ["changed", "charged", "challenged", "chatted"]},
            {"answer": "essential", "options": ["essential", "potential", "influential", "confidential"]},
            {"answer": "advance", "options": ["advance", "advantage", "adventure", "advertisement"]},
            {"answer": "maintain", "options": ["maintain", "contain", "obtain", "retain"]},
            {"answer": "lead", "options": ["lead", "led", "load", "lean"]},
            {"answer": "recommend", "options": ["recommend", "command", "comment", "commit"]},
            {"answer": "taking", "options": ["taking", "making", "getting", "putting"]},
            {"answer": "denied", "options": ["denied", "defined", "decided", "delayed"]},
            {"answer": "accessible", "options": ["accessible", "acceptable", "adjustable", "advisable"]},
            {"answer": "opportunities", "options": ["opportunities", "operations", "opinions", "oppositions"]},
        ],
    },
    2023: {
        "passage": (
            "Environmental protection has become one of the most [BLANK_0] issues of our time. "
            "Governments worldwide are taking [BLANK_1] to reduce carbon emissions and promote "
            "sustainable development. Renewable energy sources such as solar and wind power are "
            "gradually [BLANK_2] traditional fossil fuels. However, the transition to a green "
            "economy [BLANK_3] significant investment and international cooperation. Many "
            "developing countries face the [BLANK_4] of balancing economic growth with "
            "environmental protection. Scientists have [BLANK_5] that global temperatures "
            "could rise by 2 degrees Celsius by 2050 if no action is taken. This would have "
            "severe [BLANK_6] for ecosystems and human societies. On a positive note, public "
            "awareness of environmental issues has been steadily [BLANK_7]. More young people "
            "are choosing to [BLANK_8] in environmental activities and adopt eco-friendly "
            "lifestyles. The future of our planet [BLANK_9] on the choices we make today."
        ),
        "blanks": [
            {"answer": "pressing", "options": ["pressing", "passing", "processing", "professing"]},
            {"answer": "measures", "options": ["measures", "treasures", "pleasures", "pressures"]},
            {"answer": "replacing", "options": ["replacing", "repeating", "replying", "reporting"]},
            {"answer": "requires", "options": ["requires", "requests", "acquires", "inquires"]},
            {"answer": "challenge", "options": ["challenge", "channel", "chapter", "charity"]},
            {"answer": "predicted", "options": ["predicted", "prepared", "prevented", "presented"]},
            {"answer": "consequences", "options": ["consequences", "circumstances", "consciousness", "conferences"]},
            {"answer": "increasing", "options": ["increasing", "decreasing", "processing", "expressing"]},
            {"answer": "participate", "options": ["participate", "anticipate", "separate", "celebrate"]},
            {"answer": "depends", "options": ["depends", "defends", "descends", "extends"]},
        ],
    },
    2024: {
        "passage": (
            "The concept of lifelong learning has gained widespread [BLANK_0] in recent years. "
            "In a rapidly changing world, the skills that were [BLANK_1] a decade ago may no "
            "longer be relevant today. This reality has forced many professionals to [BLANK_2] "
            "their knowledge and acquire new competencies throughout their careers. Online "
            "learning platforms have made education more [BLANK_3] than ever before, allowing "
            "people to study at their own pace from anywhere in the world. However, the "
            "[BLANK_4] of online learning also presents challenges. Self-discipline and time "
            "management are [BLANK_5] skills for success in this environment. Research "
            "[BLANK_6] that learners who set specific goals and maintain a regular study "
            "schedule are more likely to complete their courses. Educational institutions are "
            "also [BLANK_7] their approaches to meet the changing needs of students. They are "
            "increasingly [BLANK_8] technology into traditional classroom settings. The "
            "boundary between formal and informal learning continues to [BLANK_9]."
        ),
        "blanks": [
            {"answer": "recognition", "options": ["recognition", "recommendation", "registration", "regulation"]},
            {"answer": "valued", "options": ["valued", "varied", "vanished", "ventured"]},
            {"answer": "update", "options": ["update", "upgrade", "upload", "upset"]},
            {"answer": "flexible", "options": ["flexible", "sensible", "possible", "visible"]},
            {"answer": "convenience", "options": ["convenience", "confidence", "conference", "conscience"]},
            {"answer": "crucial", "options": ["crucial", "casual", "criminal", "critical"]},
            {"answer": "indicates", "options": ["indicates", "dedicates", "educates", "complicates"]},
            {"answer": "adapting", "options": ["adapting", "adopting", "adjusting", "admiring"]},
            {"answer": "integrating", "options": ["integrating", "interrupting", "interpreting", "interacting"]},
            {"answer": "blur", "options": ["blur", "block", "blend", "blast"]},
        ],
    },
    2025: {
        "passage": (
            "Artificial intelligence is transforming industries at an [BLANK_0] pace. From "
            "healthcare to transportation, AI-powered systems are making decisions that were "
            "once the [BLANK_1] domain of human experts. While these advances bring remarkable "
            "benefits, they also raise important ethical questions. One major concern is the "
            "potential [BLANK_2] of jobs as machines become capable of performing tasks "
            "traditionally done by humans. Experts argue that rather than simply eliminating "
            "jobs, AI will [BLANK_3] the nature of work, creating new roles that we cannot yet "
            "imagine. Another issue is data privacy, as AI systems often [BLANK_4] on vast "
            "amounts of personal information to function effectively. Governments are working "
            "to establish [BLANK_5] that protect citizens while not stifling innovation. The "
            "key to a successful AI future lies in finding the right [BLANK_6] between progress "
            "and protection. Education systems must also [BLANK_7] to prepare students for an "
            "AI-driven world. Critical thinking and creativity will become increasingly "
            "[BLANK_8] as routine tasks are automated. Ultimately, the goal should be to "
            "use AI as a tool to [BLANK_9] human capabilities rather than replace them."
        ),
        "blanks": [
            {"answer": "unprecedented", "options": ["unprecedented", "unpredictable", "unprofessional", "unprofitable"]},
            {"answer": "exclusive", "options": ["exclusive", "excessive", "expensive", "extensive"]},
            {"answer": "displacement", "options": ["displacement", "disagreement", "disappointment", "disappearance"]},
            {"answer": "transform", "options": ["transform", "transfer", "translate", "transport"]},
            {"answer": "rely", "options": ["rely", "relay", "relax", "relate"]},
            {"answer": "regulations", "options": ["regulations", "relations", "reflections", "revolutions"]},
            {"answer": "balance", "options": ["balance", "balloon", "ballot", "ballet"]},
            {"answer": "evolve", "options": ["evolve", "involve", "resolve", "revolve"]},
            {"answer": "valuable", "options": ["valuable", "variable", "visible", "vulnerable"]},
            {"answer": "enhance", "options": ["enhance", "enlarge", "enrich", "engage"]},
        ],
    },
    2026: {
        "passage": (
            "Mental health awareness has [BLANK_0] significantly over the past decade. What was "
            "once a taboo subject is now openly discussed in many societies. This shift in "
            "attitude has been [BLANK_1] by celebrities, athletes, and public figures who have "
            "shared their personal struggles. Research has shown that regular exercise, adequate "
            "sleep, and social connections are [BLANK_2] for maintaining good mental health. "
            "Unfortunately, many people still [BLANK_3] to seek help due to the remaining stigma "
            "or lack of access to mental health services. The COVID-19 pandemic [BLANK_4] the "
            "situation, leading to increased rates of anxiety and depression worldwide. "
            "Workplaces are increasingly recognizing the importance of employee [BLANK_5] and "
            "are introducing wellness programs. Schools are also incorporating mental health "
            "education into their [BLANK_6]. Experts emphasize that mental health should be "
            "treated with the same [BLANK_7] as physical health. Simple daily practices like "
            "mindfulness and gratitude journaling can make a significant [BLANK_8]. The message "
            "is clear: seeking help is a sign of [BLANK_9], not weakness."
        ),
        "blanks": [
            {"answer": "improved", "options": ["improved", "approved", "proved", "removed"]},
            {"answer": "driven", "options": ["driven", "drawn", "drowned", "drained"]},
            {"answer": "essential", "options": ["essential", "official", "beneficial", "superficial"]},
            {"answer": "hesitate", "options": ["hesitate", "fascinate", "dominate", "illuminate"]},
            {"answer": "worsened", "options": ["worsened", "witnessed", "welcomed", "withdrawn"]},
            {"answer": "well-being", "options": ["well-being", "well-known", "well-off", "well-done"]},
            {"answer": "curriculum", "options": ["curriculum", "currency", "current", "curtain"]},
            {"answer": "priority", "options": ["priority", "property", "prosperity", "publicity"]},
            {"answer": "difference", "options": ["difference", "reference", "preference", "conference"]},
            {"answer": "strength", "options": ["strength", "stretch", "stream", "stress"]},
        ],
    },
}

# ============================================================
# Hand-crafted reading passages (2 per year, 5 questions each)
# ============================================================
READING_PASSAGES = [
    {
        "year": 2022,
        "passage": (
            "Reading is one of the most effective ways to expand one's vocabulary and improve "
            "language skills. Studies have shown that people who read regularly tend to have "
            "larger vocabularies and better writing abilities than those who do not. This is "
            "because reading exposes individuals to words and sentence structures that they "
            "might not encounter in everyday conversation. Furthermore, reading helps develop "
            "critical thinking skills by requiring readers to analyze information, make "
            "connections, and draw conclusions. In the digital age, the way people read has "
            "changed significantly. Many now prefer reading on screens rather than on paper. "
            "While digital reading offers convenience, research suggests that reading on paper "
            "may lead to better comprehension and retention of information. Regardless of the "
            "medium, the important thing is to make reading a regular habit."
        ),
        "questions": [
            {"question": "What is the main idea of this passage?", "options": ["The benefits and importance of reading", "The history of reading habits", "How to read faster", "Digital versus paper books"], "answer": "The benefits and importance of reading"},
            {"question": "According to the passage, what advantage do regular readers have?", "options": ["Larger vocabularies and better writing", "Faster reading speeds", "Better eyesight", "More free time"], "answer": "Larger vocabularies and better writing"},
            {"question": "What does the passage say about reading on screens?", "options": ["It is convenient but may reduce comprehension", "It is always better than paper", "It should be avoided completely", "It improves memory"], "answer": "It is convenient but may reduce comprehension"},
            {"question": "The word 'retention' in the passage most likely means:", "options": ["The ability to remember", "The act of removing", "The speed of reading", "The pleasure of learning"], "answer": "The ability to remember"},
            {"question": "What is the author's attitude toward reading?", "options": ["Encouraging and positive", "Critical and negative", "Neutral and indifferent", "Doubtful and uncertain"], "answer": "Encouraging and positive"},
        ],
    },
    {
        "year": 2022,
        "passage": (
            "The global tourism industry has experienced dramatic changes in recent years. "
            "Before the pandemic, international travel had reached record levels, with over "
            "1.4 billion tourist arrivals worldwide in 2019. However, the sudden halt in "
            "travel brought about by global health concerns forced the industry to rethink "
            "its approach. Many destinations are now focusing on sustainable tourism, which "
            "aims to minimize the negative impacts of travel on local environments and "
            "communities. This includes limiting visitor numbers at popular sites, promoting "
            "off-season travel, and supporting local businesses. Technology has also played "
            "a key role in the industry's recovery, with contactless check-ins, virtual tours, "
            "and digital health passes becoming commonplace. While the industry still faces "
            "challenges, there is growing optimism about its future."
        ),
        "questions": [
            {"question": "What is the main topic of this passage?", "options": ["Changes in the tourism industry", "The history of travel", "How to plan a vacation", "Airline regulations"], "answer": "Changes in the tourism industry"},
            {"question": "How many tourist arrivals were there in 2019?", "options": ["Over 1.4 billion", "Over 14 million", "Over 140 million", "Over 14 billion"], "answer": "Over 1.4 billion"},
            {"question": "What is sustainable tourism meant to do?", "options": ["Minimize negative impacts on environment and communities", "Increase hotel prices", "Reduce the number of countries tourists can visit", "Eliminate all forms of travel"], "answer": "Minimize negative impacts on environment and communities"},
            {"question": "Which technology is mentioned as becoming commonplace?", "options": ["Contactless check-ins", "Flying cars", "Robot tour guides", "Underwater hotels"], "answer": "Contactless check-ins"},
            {"question": "What is the author's tone regarding the future of tourism?", "options": ["Optimistic", "Pessimistic", "Angry", "Confused"], "answer": "Optimistic"},
        ],
    },
    {
        "year": 2023,
        "passage": (
            "The concept of remote work has transformed from a niche arrangement to a mainstream "
            "practice in just a few years. Before 2020, only a small percentage of employees "
            "worked from home regularly. Today, millions of people around the world have "
            "experienced remote work in some form. The benefits are numerous: employees save "
            "time and money on commuting, enjoy greater flexibility, and often report higher "
            "job satisfaction. Companies benefit from reduced office costs and access to a "
            "wider talent pool. However, remote work is not without its challenges. Many "
            "workers struggle with feelings of isolation and the blurring of boundaries between "
            "work and personal life. Communication can also be more difficult when team members "
            "are not in the same physical space. As organizations look to the future, many are "
            "adopting hybrid models that combine the best aspects of both in-office and remote work."
        ),
        "questions": [
            {"question": "What is the main subject of this passage?", "options": ["The rise and impact of remote work", "The history of office buildings", "Computer technology advances", "Traffic problems in cities"], "answer": "The rise and impact of remote work"},
            {"question": "Which is mentioned as a benefit of remote work for employees?", "options": ["Saving time and money on commuting", "Free office supplies", "Higher salary guaranteed", "More vacation days"], "answer": "Saving time and money on commuting"},
            {"question": "What challenge of remote work does the passage mention?", "options": ["Feelings of isolation", "Poor internet connections", "Expensive equipment", "Lack of job opportunities"], "answer": "Feelings of isolation"},
            {"question": "What are many organizations adopting for the future?", "options": ["Hybrid work models", "Fully remote only", "Office-only policies", "No work policies"], "answer": "Hybrid work models"},
            {"question": "The phrase 'blurring of boundaries' refers to:", "options": ["The mixing of work and personal life", "Poor eyesight from screens", "Unclear office rules", "Geographic borders"], "answer": "The mixing of work and personal life"},
        ],
    },
    {
        "year": 2023,
        "passage": (
            "Time management is a skill that can significantly impact one's academic and "
            "professional success. Effective time managers tend to be more productive, less "
            "stressed, and better able to achieve their goals. One popular technique is the "
            "Pomodoro method, which involves working in focused 25-minute intervals followed "
            "by short breaks. This approach helps maintain concentration and prevents burnout. "
            "Another important strategy is prioritization—identifying which tasks are most "
            "important and tackling them first. Many successful people also emphasize the "
            "importance of saying 'no' to non-essential commitments that can consume valuable "
            "time. Creating a daily or weekly schedule can provide structure and ensure that "
            "important tasks are not forgotten. While no single method works for everyone, "
            "experimenting with different approaches can help individuals find what works best."
        ),
        "questions": [
            {"question": "What is the main purpose of this passage?", "options": ["To introduce time management strategies", "To criticize poor time management", "To advertise a productivity app", "To compare different careers"], "answer": "To introduce time management strategies"},
            {"question": "What is the Pomodoro method?", "options": ["Working in 25-minute focused intervals with breaks", "Working non-stop for 8 hours", "Only working in the morning", "Taking long breaks between short work periods"], "answer": "Working in 25-minute focused intervals with breaks"},
            {"question": "What does the passage say about prioritization?", "options": ["It means doing the most important tasks first", "It means doing everything at once", "It means ignoring all tasks", "It means delegating everything"], "answer": "It means doing the most important tasks first"},
            {"question": "Why does the passage suggest saying 'no' to some commitments?", "options": ["They can consume valuable time", "They are always harmful", "They are illegal", "They cost too much money"], "answer": "They can consume valuable time"},
            {"question": "What does the author suggest about finding the right method?", "options": ["Experiment with different approaches", "Use only the Pomodoro method", "Give up if one method fails", "Copy exactly what successful people do"], "answer": "Experiment with different approaches"},
        ],
    },
    {
        "year": 2024,
        "passage": (
            "The food we eat has a profound impact not only on our health but also on the "
            "environment. The production of food accounts for about a quarter of global "
            "greenhouse gas emissions. Meat production, particularly beef, has an especially "
            "large environmental footprint due to the land, water, and feed required. In "
            "contrast, plant-based foods generally have a much lower environmental impact. "
            "This has led to growing interest in vegetarian and vegan diets, as well as "
            "innovations in plant-based meat alternatives. Reducing food waste is another "
            "crucial step. Approximately one-third of all food produced globally is wasted, "
            "which represents not only a moral concern but also an environmental one. Small "
            "changes in our eating habits, such as eating more seasonal and locally produced "
            "foods, can collectively make a significant difference for the planet."
        ),
        "questions": [
            {"question": "What is the main topic of this passage?", "options": ["The environmental impact of food", "Cooking techniques", "Restaurant reviews", "Farming history"], "answer": "The environmental impact of food"},
            {"question": "How much of global greenhouse gas emissions comes from food production?", "options": ["About a quarter", "About half", "About three quarters", "Nearly all"], "answer": "About a quarter"},
            {"question": "Why does beef have a large environmental footprint?", "options": ["It requires much land, water, and feed", "Cows produce too much milk", "Beef is expensive to buy", "Cows are difficult to transport"], "answer": "It requires much land, water, and feed"},
            {"question": "How much food is wasted globally according to the passage?", "options": ["About one-third", "About one-half", "About one-tenth", "Nearly none"], "answer": "About one-third"},
            {"question": "What small change does the passage suggest?", "options": ["Eating more seasonal and local foods", "Eating only fast food", "Never eating vegetables", "Importing all food from abroad"], "answer": "Eating more seasonal and local foods"},
        ],
    },
    {
        "year": 2024,
        "passage": (
            "The rise of e-commerce has fundamentally changed the way people shop. Traditional "
            "brick-and-mortar stores have faced increasing competition from online retailers "
            "who can offer lower prices, wider selections, and the convenience of home delivery. "
            "The COVID-19 pandemic accelerated this trend, as lockdowns forced many consumers "
            "to try online shopping for the first time. Even as restrictions have lifted, many "
            "have continued to shop online due to the habits they formed. However, physical "
            "stores still offer advantages that online retailers cannot easily replicate. "
            "Customers can see and touch products before buying, receive immediate assistance "
            "from staff, and take purchases home immediately. As a result, many successful "
            "retailers are now adopting an omnichannel approach, integrating their online and "
            "offline operations to provide a seamless shopping experience."
        ),
        "questions": [
            {"question": "What is the passage mainly about?", "options": ["The growth and impact of e-commerce", "How to start an online business", "The history of shopping malls", "Credit card payment methods"], "answer": "The growth and impact of e-commerce"},
            {"question": "What accelerated the trend toward online shopping?", "options": ["The COVID-19 pandemic", "Better weather", "Lower taxes", "New road construction"], "answer": "The COVID-19 pandemic"},
            {"question": "What advantage do physical stores have over online shops?", "options": ["Customers can see and touch products before buying", "They are always cheaper", "They are open 24 hours", "They have more products"], "answer": "Customers can see and touch products before buying"},
            {"question": "What approach are many retailers now adopting?", "options": ["Omnichannel (integrating online and offline)", "Online only", "Physical stores only", "Mail order catalogs"], "answer": "Omnichannel (integrating online and offline)"},
            {"question": "The word 'seamless' in the passage most likely means:", "options": ["Smooth and continuous", "Rough and difficult", "Separate and divided", "Slow and careful"], "answer": "Smooth and continuous"},
        ],
    },
    {
        "year": 2025,
        "passage": (
            "Social media has become an integral part of modern life, connecting billions of "
            "people worldwide. Platforms like WeChat, Weibo, and Douyin have transformed how "
            "people share information, express opinions, and build communities. For businesses, "
            "social media offers powerful tools for marketing and customer engagement. However, "
            "the widespread use of social media has also raised concerns. Research has linked "
            "excessive social media use to increased rates of anxiety and depression, "
            "particularly among young people. The spread of misinformation is another serious "
            "problem, as false information can travel faster and reach more people than "
            "verified facts. In response, many platforms have introduced fact-checking "
            "features and content moderation policies. The challenge remains to enjoy the "
            "benefits of social media while minimizing its harmful effects."
        ),
        "questions": [
            {"question": "What is the main idea of this passage?", "options": ["Both benefits and drawbacks of social media", "How to become a social media influencer", "The history of the internet", "Mobile phone technology"], "answer": "Both benefits and drawbacks of social media"},
            {"question": "What concern about social media use does the passage mention?", "options": ["Increased anxiety and depression among young people", "Higher phone bills", "Slower internet speeds", "Fewer job opportunities"], "answer": "Increased anxiety and depression among young people"},
            {"question": "What problem does the passage mention about information on social media?", "options": ["Misinformation spreads rapidly", "Information is always accurate", "There is too little information", "Information is too expensive"], "answer": "Misinformation spreads rapidly"},
            {"question": "What have platforms done in response to concerns?", "options": ["Introduced fact-checking features", "Shut down completely", "Removed all user content", "Increased prices"], "answer": "Introduced fact-checking features"},
            {"question": "What is the author's overall position on social media?", "options": ["Balanced—recognizing both pros and cons", "Entirely negative and critical", "Completely positive and supportive", "Uninterested and dismissive"], "answer": "Balanced—recognizing both pros and cons"},
        ],
    },
    {
        "year": 2025,
        "passage": (
            "Volunteering is an activity that benefits both the community and the individual "
            "volunteer. People who volunteer regularly report higher levels of happiness and "
            "life satisfaction compared to those who do not. This may be because helping others "
            "provides a sense of purpose and connection. Volunteering can also help individuals "
            "develop new skills and gain valuable work experience. For students, volunteer work "
            "can strengthen college applications and resumes. There are many ways to get "
            "involved, from tutoring children and visiting elderly people to participating in "
            "environmental clean-up projects. Even small acts of service, such as helping a "
            "neighbor or donating unused items, can make a difference. The key is to find a "
            "cause that aligns with one's interests and values. As the saying goes, 'The best "
            "way to find yourself is to lose yourself in the service of others.'"
        ),
        "questions": [
            {"question": "What is the main subject of this passage?", "options": ["The benefits of volunteering", "How to find a paid job", "The history of charity organizations", "Government social programs"], "answer": "The benefits of volunteering"},
            {"question": "What do regular volunteers report according to the passage?", "options": ["Higher levels of happiness and life satisfaction", "More money and possessions", "Better physical health only", "Less free time"], "answer": "Higher levels of happiness and life satisfaction"},
            {"question": "How can volunteering help students?", "options": ["Strengthen college applications and resumes", "Guarantee admission to top universities", "Replace the need for studying", "Provide free housing"], "answer": "Strengthen college applications and resumes"},
            {"question": "What examples of volunteering are mentioned?", "options": ["Tutoring children and visiting elderly people", "Watching television and playing games", "Shopping and traveling", "Sleeping and resting"], "answer": "Tutoring children and visiting elderly people"},
            {"question": "What does the author suggest as the key to volunteering?", "options": ["Finding a cause matching one's interests and values", "Only volunteering for money", "Avoiding all community activities", "Volunteering as little as possible"], "answer": "Finding a cause matching one's interests and values"},
        ],
    },
    {
        "year": 2026,
        "passage": (
            "Artificial intelligence is rapidly changing the landscape of education. AI-powered "
            "tools can now personalize learning experiences by adapting to each student's pace "
            "and learning style. For example, intelligent tutoring systems can identify areas "
            "where a student is struggling and provide targeted practice exercises. Language "
            "learning apps use AI to correct pronunciation and suggest vocabulary based on the "
            "learner's level. However, the integration of AI in education also raises concerns. "
            "Some educators worry that over-reliance on technology could reduce human "
            "interaction, which is essential for developing social and emotional skills. There "
            "are also concerns about data privacy and the potential for AI to reinforce existing "
            "biases. The challenge for educators is to use AI as a supplement to, rather than "
            "a replacement for, traditional teaching methods. When used thoughtfully, AI has "
            "the potential to make quality education more accessible to learners everywhere."
        ),
        "questions": [
            {"question": "What is the main topic of this passage?", "options": ["The role of AI in education", "The history of computers", "How to build AI systems", "The future of robots"], "answer": "The role of AI in education"},
            {"question": "How can AI personalize learning according to the passage?", "options": ["By adapting to each student's pace and style", "By teaching all students the same way", "By replacing all teachers", "By giving everyone the same grade"], "answer": "By adapting to each student's pace and style"},
            {"question": "What concern about AI in education is mentioned?", "options": ["Reduced human interaction affecting social skills", "Increased cost of pencils", "Students becoming too athletic", "Schools getting too small"], "answer": "Reduced human interaction affecting social skills"},
            {"question": "How does the author suggest AI should be used in education?", "options": ["As a supplement to traditional teaching", "As a complete replacement for teachers", "Not at all in any form", "Only in universities"], "answer": "As a supplement to traditional teaching"},
            {"question": "What potential benefit of AI does the author highlight at the end?", "options": ["Making quality education more accessible", "Eliminating the need for schools", "Guaranteeing perfect grades", "Replacing all textbooks"], "answer": "Making quality education more accessible"},
        ],
    },
    {
        "year": 2026,
        "passage": (
            "The concept of minimalism has gained popularity as a lifestyle choice in recent "
            "years. At its core, minimalism is about intentionally living with fewer material "
            "possessions and focusing on what truly matters. Proponents of minimalism argue "
            "that reducing clutter—both physical and mental—can lead to greater clarity, "
            "reduced stress, and increased happiness. Many minimalists report feeling freer "
            "and more in control of their lives after simplifying their environments. The "
            "movement is not about deprivation or living with nothing; rather, it encourages "
            "people to be more mindful about what they own and why. From decluttering homes "
            "to simplifying schedules, minimalism can be applied to many aspects of life. "
            "Critics argue that minimalism is a privilege that not everyone can afford, but "
            "supporters counter that the philosophy is adaptable to different circumstances "
            "and budgets. The core message is universal: less can indeed be more."
        ),
        "questions": [
            {"question": "What is the main idea of this passage?", "options": ["Minimalism as a lifestyle focused on what truly matters", "How to make more money", "The history of furniture design", "How to decorate a large house"], "answer": "Minimalism as a lifestyle focused on what truly matters"},
            {"question": "What benefits of minimalism are mentioned?", "options": ["Greater clarity, reduced stress, increased happiness", "More possessions and larger homes", "Higher income and better jobs", "Faster cars and more travel"], "answer": "Greater clarity, reduced stress, increased happiness"},
            {"question": "What does the passage say minimalism is NOT about?", "options": ["Deprivation or living with nothing", "Being mindful about possessions", "Simplifying one's environment", "Reducing clutter"], "answer": "Deprivation or living with nothing"},
            {"question": "What criticism of minimalism is mentioned?", "options": ["It is a privilege not everyone can afford", "It is illegal in some countries", "It damages the economy", "It makes people unhappy"], "answer": "It is a privilege not everyone can afford"},
            {"question": "What is the core message of minimalism according to the passage?", "options": ["Less can be more", "More is always better", "Money buys happiness", "Never throw anything away"], "answer": "Less can be more"},
        ],
    },
]

# ============================================================
# Writing prompts (1 per year)
# ============================================================
WRITING_PROMPTS = {
    2022: {
        "topic": "The Importance of Reading",
        "outline": "1. 阅读的重要性；2. 现代社会中阅读习惯的变化；3. 如何培养良好的阅读习惯",
        "suggested_words": ["reading", "vocabulary", "knowledge", "habit", "concentration"],
        "word_limit": 150,
    },
    2023: {
        "topic": "Environmental Protection",
        "outline": "1. 当前面临的环境问题；2. 个人可以为环保做什么；3. 你的看法和建议",
        "suggested_words": ["environment", "protection", "pollution", "sustainable", "recycle"],
        "word_limit": 150,
    },
    2024: {
        "topic": "Online Learning",
        "outline": "1. 在线学习的优势；2. 在线学习的挑战；3. 你对在线学习的看法",
        "suggested_words": ["online", "learning", "flexible", "convenient", "discipline"],
        "word_limit": 150,
    },
    2025: {
        "topic": "The Impact of Social Media",
        "outline": "1. 社交媒体的普及；2. 社交媒体对生活的影响（正面和负面）；3. 如何合理使用社交媒体",
        "suggested_words": ["social", "media", "communication", "influence", "balance"],
        "word_limit": 150,
    },
    2026: {
        "topic": "The Future of Work",
        "outline": "1. 人工智能对工作的影响；2. 未来需要什么样的人才；3. 你应该如何准备",
        "suggested_words": ["artificial", "intelligence", "career", "skill", "adapt"],
        "word_limit": 150,
    },
}

# ============================================================
# Seed function
# ============================================================
def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Deduplicate: remove duplicate papers for the same year (keep lowest id)
    from sqlalchemy import func as sqlfunc
    dupes = (
        db.query(ExamPaper.year, sqlfunc.count(ExamPaper.id))
        .group_by(ExamPaper.year)
        .having(sqlfunc.count(ExamPaper.id) > 1)
        .all()
    )
    for year, _ in dupes:
        ids = [row[0] for row in db.query(ExamPaper.id).filter(ExamPaper.year == year).order_by(ExamPaper.id).all()]
        keep, remove = ids[0], ids[1:]
        for rid in remove:
            db.query(ExamQuestion).filter(ExamQuestion.paper_id == rid).delete()
            db.query(ExamHistory).filter(ExamHistory.paper_id == rid).delete()
            db.query(ExamPaper).filter(ExamPaper.id == rid).delete()
        print(f"Deduped {year}: kept id={keep}, removed ids={remove}")
    if dupes:
        db.commit()

    all_words = db.query(Word).all()
    if len(all_words) < 30:
        print(f"Only {len(all_words)} words in DB, need at least 30 for exam generation.")
        db.close()
        return

    years_to_seed = [2022, 2023, 2024, 2025, 2026]
    existing_years = {row[0] for row in db.query(ExamPaper.year).filter(ExamPaper.year.in_(years_to_seed)).all()}
    missing_years = [y for y in years_to_seed if y not in existing_years]

    if not missing_years:
        print("All exam papers already exist, skipping seed.")
        db.close()
        return

    for year in missing_years:
        print(f"Generating paper for {year}...")

        paper = ExamPaper(
            title=f"{year}年CET-4模拟真题",
            year=year,
            description=f"{year}年大学英语四级考试模拟试卷，共51道选择题+1篇作文，限时120分钟",
            time_limit=120,
        )
        db.add(paper)
        db.flush()

        order = 1

        # Section A: Vocab (30 questions)
        vocab_words = random.sample(all_words, 30)
        for word in vocab_words:
            distractors = [w for w in all_words if w.id != word.id]
            chosen_distractors = random.sample(distractors, min(3, len(distractors)))
            options = [word.chinese] + [d.chinese for d in chosen_distractors]
            random.shuffle(options)
            db.add(ExamQuestion(
                paper_id=paper.id,
                question_type="vocab",
                question_text=f"What is the meaning of '{word.english}'?",
                options=options,
                correct_answer=word.chinese,
                word_id=word.id,
                order_num=order,
            ))
            order += 1

        # Section B: Cloze (10 questions)
        if year in CLOZE_TEMPLATES:
            cloze = CLOZE_TEMPLATES[year]
            for i, blank in enumerate(cloze["blanks"]):
                passage_text = cloze["passage"]
                # Render blanks in the passage
                for j, b in enumerate(cloze["blanks"]):
                    passage_text = passage_text.replace(f"[BLANK_{j}]", f"[{j+1}]")
                db.add(ExamQuestion(
                    paper_id=paper.id,
                    question_type="cloze",
                    passage=passage_text,
                    question_text=f"Question {i+1}: Choose the best word for blank [{i+1}].",
                    options=blank["options"],
                    correct_answer=blank["answer"],
                    word_id=None,
                    order_num=order,
                ))
                order += 1

        # Section C: Reading (10 questions)
        year_passages = [rp for rp in READING_PASSAGES if rp["year"] == year]
        for rp in year_passages:
            for q in rp["questions"]:
                db.add(ExamQuestion(
                    paper_id=paper.id,
                    question_type="reading",
                    passage=rp["passage"],
                    question_text=q["question"],
                    options=q["options"],
                    correct_answer=q["answer"],
                    word_id=None,
                    order_num=order,
                ))
                order += 1

        # Section D: Writing (1 question, not auto-graded)
        if year in WRITING_PROMPTS:
            wp = WRITING_PROMPTS[year]
            prompt_parts = [f"Topic: {wp['topic']}"]
            if wp.get("outline"):
                prompt_parts.append(f"Outline: {wp['outline']}")
            if wp.get("suggested_words"):
                prompt_parts.append(f"Suggested vocabulary: {', '.join(wp['suggested_words'])}")
            if wp.get("word_limit"):
                prompt_parts.append(f"Word limit: {wp['word_limit']} words")

            # Store writing prompt metadata as JSON in options
            db.add(ExamQuestion(
                paper_id=paper.id,
                question_type="writing",
                passage=None,
                question_text="\n".join(prompt_parts),
                options=[wp.get("topic", ""), wp.get("outline", ""),
                         ", ".join(wp.get("suggested_words", [])), str(wp.get("word_limit", 150))],
                correct_answer="",  # Writing is not auto-graded
                word_id=None,
                order_num=order,
            ))
            order += 1

    db.commit()
    print(f"Done! Generated 5 papers with {order - 1} total items each.")
    db.close()


if __name__ == "__main__":
    seed()
