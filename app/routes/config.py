# Модели и переменные
MODEL_NAME = "gpt-3.5-turbo"
TRAIN_COLUMNS = [
    'category_target_encoding', 'create_launch', 'launch_deadline', 'goal',
    'staff_pick', 'Nums_created', 'launch_month_encoded', 'name_len',
    'market_adaptability', 'launch_weekday_encoded',
    'execution_capabilities', 'creator_experience', 'market_size',
    'product_market_fit', 'Nums_backed', 'cutting_edge_technology',
    'development_pace', 'innovation_mentions', 'visionary_ability'
]


CATEGORY_MAPPINGS = {
        "industry_growth": ["No", "No answer", "Yes"],
        "market_size": ["Small", "Medium", "Large", "No answer"],
        "development_pace": ["Slower", "Same", "Faster", "No answer"],
        "market_adaptability": ["Not Adaptable", "Somewhat Adaptable", "Very Adaptable", "No answer"],
        "execution_capabilities": ["Poor", "Average", "Excellent", "No answer"],
        "investor_backing": ["Unknown", "Recognized", "Highly Regarded", "No answer"],
        "product_market_fit": ["Weak", "Moderate", "Strong", "No answer"],
        "sentiment_analysis": ["Negative", "Neutral", "Positive", "No answer"],
        "innovation_mentions": ["Rarely", "Sometimes", "Often", "No answer"],
        "cutting_edge_technology": ["No", "Mentioned", "Emphasized", "No answer"],
        "timing": ["Too Early", "Just Right", "Too Late", "No answer"],
        "creator_experience": ["Low", "Medium", "High", "No answer"],
        "visionary_ability": ['Limited', 'Moderate', 'Strong', 'No answer'],
        "creator_leadership": ['Weak', 'Average', 'Strong', 'No answer']
}

MODEL_CONTENT_PREPROC = '''
Analyze the startup based on the following criteria. Answer each question using only one of the predefined categories. Only return the JSON response based on your analysis, and do not repeat this instruction or provide any other text.

Questions:
1) "Is the startup operating in a growing industry?"
2) "Is the market size of the startup's product/service considered large?"
3) "Does the startup demonstrate rapid growth compared to competitors?"
4) "Is the startup considered adaptable to market changes?"
5) "How do you assess the startup's execution capabilities?"
6) "Are well-known investors or venture firms backing the startup?"
7) "Do market research indicate a strong product-market fit for the startup?"
8) "Does sentiment analysis of founder and company descriptions suggest high positivity?"
9) "Are innovations frequently mentioned in public company communications?"
10) "Does the startup mention cutting-edge technologies in its descriptions?"
11) "Given the startup's industry and current market conditions (or conditions at the time of founding), is it the right time for the startup's product or service?"
12) "How experienced is startup's execution?"
13) "Is the creator capable of envisioning strategic development?"
14) "How are the creator's management skills assessed?"

Answer using the following options:
1)[Yes/No/No answer]
2)[Small/Medium/Large/No answer]
3)[Slower/Same/Faster/No answer]
4)[Not adaptable/Relatively adaptable/Very adaptable/No answer]
5)[Poor/Average/Excellent/No answer]
6)[Unknown/Known/Highly valued/No answer]
7)[Weak/Moderate/Strong/No answer]
8)[Negative/Neutral/Positive/No answer]
9)[Rarely/Sometimes/Often/No answer]
10)[No/Mentioned/Highlighted/No answer]
11)[Too early/Just right/Too late/No answer]
12)[Low/Medium/High/No answer]
13)[Limited/Moderate/Strong/No answer]
14)[Weak/Average/Strong/No answer]

Respond only in the following JSON format based on your analysis (with new values, not repeating this instruction), **in English**:
{
    "startup_analysis_responses": {
        "industry_growth": "Your answer",
        "market_size": "Your answer",
        "development_pace": "Your answer",
        "market_adaptability": "Your answer",
        "execution_capabilities": "Your answer",
        "investor_backing": "Your answer",
        "product_market_fit": "Your answer",
        "sentiment_analysis": "Your answer",
        "innovation_mentions": "Your answer",
        "cutting_edge_technology": "Your answer",
        "timing": "Your answer",
        "creator_experience": "Your answer",
        "visionary_ability": "Your answer",
        "creator_leadership": "Your answer"
    }
}
'''