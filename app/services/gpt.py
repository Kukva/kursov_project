import openai
import json
from g4f.client import Client
import pandas as pd
from fastapi import HTTPException
from databases.config import get_settings
import joblib
import asyncio

settings = get_settings()

def get_response(sys_content: str, usr_content: str, model: str):
    client = Client()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_content},
            {"role": "user", "content": usr_content}
        ],
    )
    return completion.choices[0].message.content


def process_row(row, sys_content, model):
    categories = get_response(sys_content, row, model)
    if categories:
        try:
            # Пробуем распарсить JSON
            startup_info = json.loads(categories)
            return startup_info  # Возвращаем индекс и данные
        except json.JSONDecodeError:
            # Если ошибка JSON, возвращаем индекс и None
            return None  
    return None 

def load_encoder_rf(path):
    """Загружает кодировщик из файла"""
    return joblib.load(path)

def load_model(path):
    """Загружает обученную модель"""
    return joblib.load(path)

def load_mean_dict(path):
    """Загружает закодированные по среднему категории"""
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def preprocess_features(data, category_mean):
    """Преобразовывает и подготовливает данные"""
    features = {}
    features['Nums_backed'] = int(data['num_projects_backed'])
    features['Nums_created'] = int(data['num_projects_created'])
    features['goal'] = int(data['goal_amount'])
    features['staff_pick'] = int(data['staff_pick'])
    features['name_len'] = len(data['project_name'].split())

    features['category_target_encoding'] = category_mean.get(data['category'], 0.5)

    # Преобразование дат
    create_date = pd.to_datetime(data['created_date'])
    launch_date = pd.to_datetime(data['launch_date'])
    deadline_date = pd.to_datetime(data['deadline_date'])
    features['create_launch'] = (launch_date - create_date).days
    features['launch_deadline'] = (deadline_date - launch_date).days
    features['launch_month_encoded'] = launch_date.month
    features['launch_weekday_encoded'] = launch_date.weekday()

    return features

def process_startup_info(data: dict, sys_content: str, model_name: str) -> dict:
    """Processes the startup description and returns GPT analysis asynchronously."""
    startup_info = "Startup Description: " + data['project_description'] + " Founder Information: " + data['creator_description']
    json_data = process_row(startup_info, sys_content, model_name)

    # Retry until valid response is obtained
    while json_data is None:
        json_data = process_row(startup_info, sys_content, model_name)

    return json_data

def desc_analyse(desc: str, sys_content: str, model_name: str) -> str:
    """Analyze description by summarized new features"""
    result = get_response(sys_content, desc, model_name)
    return result

def ready_features(data: dict, encoder, category_mean: dict, model_content: str, model_name: str, train_columns: list, category_mapp: dict) -> pd.DataFrame:
    """Filters the data and prepares it for model fitting."""
    json_data = process_startup_info(data, model_content, model_name)
    print("----------------Вызван получение json----------------------")
    
    # Process startup data
    if 'startup_analysis_responses' in json_data:
        startup_analysis_responses = json_data['startup_analysis_responses']
        json_df = pd.DataFrame([startup_analysis_responses])
    else:
        raise HTTPException(status_code=400, detail="'startup_analysis_responses' key not found in json_data.")

    for column, categories in category_mapp.items():
        json_df[column] = json_df[column].apply(lambda x: x if x in categories else "No answer")

    encoded_data = encoder.transform(json_df)[0]
    combined_df = pd.DataFrame({**dict(zip(json_df.columns, encoded_data)), **preprocess_features(data, category_mean)}, index=[0])

    # Filter columns
    filtered_dict = {key: combined_df[key] for key in train_columns if key in combined_df}
    return filtered_dict, json_df

def creator_analysis(startup_info, mode, model):
    analysis_prompt = (
        "You are a top-tier startup founder analyst, assessing a new founding team. Your task is to evaluate the "
        "founders based on their ability to execute, their experience, and their vision for the company. Here's "
        "the context you need to analyze:\n\n"
        "- Execution Capabilities: {execution_capabilities}\n"
        "- Creator Experience: {creator_experience}\n"
        "- Visionary Ability: {visionary_ability}\n"
        "- Market Adaptability: {market_adaptability}\n"
        "- Team Dynamics: {team_dynamics}\n\n"
        "Please provide a detailed assessment of the founders' strengths, weaknesses, and overall readiness to "
        "lead the startup to success. Evaluate their competency on a scale from 1 to 10, focusing on how their "
        "abilities align with the demands of the industry and the startup's vision. Break down each factor and "
        "offer specific insights into potential risks and opportunities. Consider any available online presence "
        "or market reputation if applicable."
    ).format(
        execution_capabilities=startup_info.get('execution_capabilities', ''),
        creator_experience=startup_info.get('creator_experience', ''),
        visionary_ability=startup_info.get('visionary_ability', ''),
        market_adaptability=startup_info.get('market_adaptability', ''),
        team_dynamics=startup_info.get('team_dynamics', '')
    )
    if mode == "simple":
        pass

    return (get_response("Please think and analyze step by step and take a deep breath.", analysis_prompt, model))


def product_analysis(startup_info, mode, model):
    analysis_prompt = (
        "You are an expert product analyst known for evaluating cutting-edge technology solutions. Today, "
        "you’re tasked with analyzing a startup's product, focusing on key aspects such as market potential, "
        "development progress, and innovation. Based on the information provided below, assess the following:\n\n"
        "- Market Size: {market_size}\n"
        "- Development Pace: {development_pace}\n"
        "- Market Adaptability: {market_adaptability}\n"
        "- Product-Market Fit: {product_market_fit}\n"
        "- Innovation Mentions: {innovation_mentions}\n"
        "- Cutting-Edge Technology: {cutting_edge_technology}\n\n"
        "Additionally, consider user reviews and feedback from platforms such as ProductHunt and G2Crowd to "
        "gauge real-world reception. Incorporate web traffic trends to reflect growing interest and market "
        "traction.\n\n"
        "Provide a comprehensive analysis, ending with a Product Viability Score (1-10) based on the product's "
        "current standing and potential for future growth. Highlight any strengths, risks, or areas of improvement."
    ).format(
        market_size=startup_info.get('market_size', 'unknown'),
        development_pace=startup_info.get('development_pace', 'growing steadily'),
        market_adaptability=startup_info.get('market_adaptability', 'unknown'),
        product_market_fit=startup_info.get('product_market_fit', 'average'),
        innovation_mentions=startup_info.get('innovation_mentions', 'minimal'),
        cutting_edge_technology=startup_info.get('cutting_edge_technology', 'average')
    )
    
    if mode == "simple":
        pass  # Implement logic for the simple mode analysis

    if mode == "advanced":
        pass  # Implement logic for the advanced mode analysis

    return (get_response(analysis_prompt, "Please think and analyze step by step.", model))

def integrate_analyses(product_info, founder_info, prediction, pred_succ, mode, model):
    prompt = """
    Imagine you are a top startup consultant. Your task is to provide the founders with specific recommendations based on the analysis of their product and founding team. The goal is to offer detailed and actionable feedback to help them improve their crowdfunding campaign, achieve better positioning, and increase their chances of success in the market. These recommendations should directly address common challenges such as incorrect project positioning, unclear goals, and weak audience engagement.

    Your recommendation must follow this structure:

    Product Feedback: Evaluate the product, highlighting strengths and weaknesses, and suggest improvements that will make the project more appealing to backers. Focus on how the product can stand out in the competitive market.
    Founder Feedback: Assess the founding team, taking into account their skills and experience. Provide suggestions on how to strengthen the team or their strategy to better meet campaign goals.
    Actionable Advice: Provide specific, practical advice for improving the project, audience engagement, and overall chances of success on crowdfunding platforms like Kickstarter.

    Example 1:
    Product Feedback: The product scores 7.5/10 for innovation but lacks differentiation in a crowded market. Refining the unique selling points and targeting niche markets could help. Explore partnerships with influencers to boost brand visibility and trust.
    Founder Feedback: The team scores 8.8/10 for experience, but execution capabilities need improvement. Hiring operational talent and focusing on partnerships could accelerate market entry.
    Actionable Advice: Prioritize finding product-market fit by conducting deeper customer research and iterating based on user feedback. Enhance operational execution to gain traction quickly.

    Example 2:
    Product Feedback: The product scores 6.3/10, with scalability concerns. Simplifying the MVP feature set and improving infrastructure for growth would help.
    Founder Feedback: The team scores 7.1/10 for passion and technical skills but lacks business acumen. Bringing in an advisor with business expertise could enhance scaling strategies.
    Actionable Advice: Simplify the product for short-term growth, and focus on mentoring from experienced entrepreneurs to guide business development and investor relations.

    Now, analyze the following data and provide tailored recommendations based on this structure
    """

    user_prompt = (
        '''
        As a startup consultant, you are providing expert recommendations to the founders based on the analysis of their product and team. The founders are struggling to reach their crowdfunding goals due to issues like incorrect positioning, unclear goals, and weak audience engagement. Your advice will help them address these challenges and improve their chances of success.
        Here is what we have:

        Product Viability: {product_info}
        Founder Competency: {founder_info}
        Using this information, provide detailed, actionable advice for the founders. Focus on the following key areas:

        Product Feedback: Evaluate the product, noting its strengths and areas for improvement. Suggest how it can stand out and become more attractive to potential backers.
        Founder Feedback: Assess the founding team’s skills and experience. Offer recommendations on how they can strengthen their execution capabilities and strategy.
        Actionable Advice: Provide specific, practical steps for improving their project description, campaign goals, and audience engagement. Ensure your feedback is constructive and focuses on enhancing their positioning and strategy to maximize success.
        Your feedback should be professional, detailed, and invaluable for startup founders looking to refine their approach.'''
    ).format(
        product_info=product_info,
        founder_info=founder_info,
    )

    if mode == "advanced":
        prediction_prompt = f"\nAdditionally, your model has predicted a {prediction}. Its a {pred_succ} likehood success. Use this prediction to guide your advice, but remember to focus on actionable steps the founders can take to improve their chances."
        user_prompt += prediction_prompt

    return get_response(prompt, user_prompt, model)