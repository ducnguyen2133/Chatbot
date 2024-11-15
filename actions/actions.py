# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Tuple
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random



# Load the product data from the Excel file
df = pd.read_excel('F:\\Project\\Chatbot\\data_hunonic.xlsx')

# Khởi tạo TF-IDF Vectorizer và ma trận TF-IDF toàn cục
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['Tên sản phẩm'].astype(str))

def get_best_matching_product(product_name: str, df: pd.DataFrame) -> Tuple[str, str]:
    ##"""Tìm sản phẩm gần đúng nhất trong DataFrame dựa trên TF-IDF."""
    # Tính toán TF-IDF cho tên sản phẩm nhập vào
    query_tfidf = vectorizer.transform([product_name])
    # Tính toán độ tương đồng cosine với tất cả các sản phẩm
    cosine_similarities = cosine_similarity(query_tfidf, tfidf_matrix).flatten()
    # Lấy chỉ số sản phẩm có độ tương đồng cao nhất
    best_match_index = cosine_similarities.argmax()
    # Lấy dữ liệu sản phẩm phù hợp nhất
    product_data = df.iloc[[best_match_index]]
    full_product_name = product_data.iloc[0]['Tên sản phẩm']
    return full_product_name, best_match_index
    
class ActionGetProduct(Action):
    def name(self) -> str:
        return "action_get_product"
    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()

        product_type_mapping = {
            "ask_aptomat": "Aptomat",
            "ask_sensor_product": "Cảm biến",
            "ask_controller_product": "Điều khiển",
            "ask_camera_product": "Camera",
            "ask_switch_bluetooth": "Công tắc Bluetooth",
            "ask_switch_resistance": "Công tắc chống giật",
            "ask_switch_touch": "Công tắc cảm ứng",
            "ask_switch_stair": "Công tắc cầu thang",
            "ask_switch_cuon": "Công tắc cửa cuốn",
            "ask_auto_pump": "Bơm tưới tự động",
            "ask_switch_wifi" : "Công tắc Wifi",
            "ask_smart_lock": "Khóa thông minh",
            "ask_light_bulb": "Đui đèn",
            "ask_curtain": "Rèm",
            "ask_socket_datic": "Ổ cắm Datic",
            "ask_anti_shock_socket": "Ổ cắm chống giật",
            "ask_socket_smart": "Ổ cắm thông minh"
        }
        
        # Get the corresponding product type
        product_type = product_type_mapping.get(intent, None)
        if not product_type:
            dispatcher.utter_message(text="Chúng tôi không có loại sản phẩm như bạn hỏi.")
            return []
        
        # Filter the DataFrame for the relevant products
        filtered_df = df[df['Loại sản phẩm'].str.contains(product_type, na=False)]
        if filtered_df.empty:
            dispatcher.utter_message(text=f"Xin lỗi, chúng tôi không có sản phẩm '{product_type}' mà bạn tìm kiếm.")
            return []
        
        # Randomly sample up to 5 products    
        n = min(5, len(filtered_df))  
        sample_product = filtered_df.sample(n=n)

        product_names = sample_product['Tên sản phẩm'].tolist() 
        product_message = "\n".join([f"{i+1}. {name}" for i, name in enumerate(product_names)])

        dispatcher.utter_message(text=f"Hiện tại chúng tôi có một số sản phẩm bạn có thể tham khảo với loại mà bạn tìm kiếm như: \n{product_message}")

        return []    
    
class ActionGetProductPrice(Action): 
    def name(self) -> Text:
        return "action_get_product_price"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy tên sản phẩm từ slot 'product'
        product_name = tracker.get_slot("product")

        # Kiểm tra nếu product_name là danh sách và lấy phần tử đầu tiên
        if isinstance(product_name, list):
            product_name = product_name[0]

        # Làm sạch tên sản phẩm
        product_name = product_name.strip()

        full_product_name, best_match_index = get_best_matching_product(product_name, df)
        product_data = df.iloc[[best_match_index]]

        if product_data.empty:
            dispatcher.utter_message(text="Xin lỗi, giá của sản phẩm này chưa được cập nhật.")
            return []
        
        price = product_data.iloc[0]['Giá']
        dispatcher.utter_message(text=f"Giá của {full_product_name} là: {price}")
        return []

class ActionGetProductFeatures(Action):
    def name(self) -> Text:
        return "action_get_product_features"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy tên sản phẩm từ slot 'product'
        product_name = tracker.get_slot("product")

        if isinstance(product_name, list):
            product_name = product_name[0]

        product_name = product_name.strip()

        # Sử dụng hàm để tìm sản phẩm gần đúng
        full_product_name, best_match_index = get_best_matching_product(product_name, df)
        product_data = df.iloc[[best_match_index]]

        if product_data.empty:
            dispatcher.utter_message(text="Xin lỗi, toi chưa cập nhật tính năng của sản phẩm này.")
            return []

        # Kiểm tra xem tính năng có tồn tại không
        features = product_data.iloc[0]['Tính năng']
        if pd.isna(features) or features == "":
            dispatcher.utter_message(text=f"Xin lỗi, hiện tại chúng tôi cập nhật tính năng cho sản phẩm {full_product_name}.")
        else:
            response = f"Tính năng của {full_product_name}: \n{features}"
            dispatcher.utter_message(text=response)
        
        return []

class ActionGetProductLink(Action):
    def name(self) -> Text:
        return "action_get_product_link"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy tên sản phẩm từ slot 'product'
        product_name = tracker.get_slot("product")

        if isinstance(product_name, list):
            product_name = product_name[0]

        product_name = product_name.strip()

        full_product_name, best_match_index = get_best_matching_product(product_name, df)
        product_data = df.iloc[[best_match_index]]

        if product_data.empty:
            dispatcher.utter_message(text="Xin lỗi, chưa có đường dẫn cho sản phẩm này.")
            return []
        
        product_link = product_data.iloc[0]['Link sản phẩm']
        dispatcher.utter_message(text=f"Đây là đường dẫn của {full_product_name}: \n{product_link}")
        return []
    
class ActionGetProductTechnicalSpecs(Action):
    def name(self) -> Text:
        return "action_get_product_technical_specs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy tên sản phẩm từ slot 'product'
        product_name = tracker.get_slot("product")

        if isinstance(product_name, list):
            product_name = product_name[0]

        product_name = product_name.strip()

        # Sử dụng hàm để tìm sản phẩm gần đúng
        full_product_name, best_match_index = get_best_matching_product(product_name, df)
        product_data = df.iloc[[best_match_index]]

        if product_data.empty:
            dispatcher.utter_message(text="Xin lỗi, thông số kỹ thuật của sản phẩm này chưa cập nhật.")
            return []

        # Kiểm tra xem thông số kỹ thuật có tồn tại không
        technical_specs = product_data.iloc[0]['Thông số kỹ thuật']
        if pd.isna(technical_specs) or technical_specs == "":
            dispatcher.utter_message(text=f"Xin lỗi, hiện tại chúng tôi chưa cập nhật thông số kỹ thuật cho sản phẩm {full_product_name}.")
        else:
            dispatcher.utter_message(text=f"Thông số kỹ thuật của {full_product_name}: \n{technical_specs}")
        
        return []
    






































    
# class ActionGetProductPrice(Action):
#     def name(self) -> Text:
#         return "action_get_product_price"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # Lấy tên sản phẩm từ slot 'product'
#         product_name = tracker.get_slot("product")

#         # Kiểm tra nếu product_name là danh sách và lấy phần tử đầu tiên
#         if isinstance(product_name, list):
#             product_name = product_name[0]

#         # Làm sạch tên sản phẩm, bỏ khoảng trắng đầu và cuối
#         product_name = product_name.strip()

#         # Tìm sản phẩm theo tên, sử dụng regular expression để tìm gần đúng
#         product_data = df[df['Tên sản phẩm'].str.contains(product_name, case=False, na=False, regex=True)]

#         if product_data.empty:
#             dispatcher.utter_message(text="Xin lỗi, tôi không tìm thấy giá của sản phẩm này.")
#             return []
        
#         # Lấy tên đầy đủ của sản phẩm
#         full_product_name = product_data.iloc[0]['Tên sản phẩm']
#         # Lấy giá của sản phẩm
#         price = product_data.iloc[0]['Giá']
#         dispatcher.utter_message(text=f"Giá của {full_product_name} là: {price}")
#         return []

# class ActionGetProductFeatures(Action):
#     def name(self) -> Text:
#         return "action_get_product_features"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # Lấy tên sản phẩm từ slot 'product'
#         product_name = tracker.get_slot("product")

#         # Kiểm tra nếu product_name là danh sách và lấy phần tử đầu tiên
#         if isinstance(product_name, list):
#             product_name = product_name[0]

#         # Tìm sản phẩm theo tên
#         product_data = df[df['Tên sản phẩm'].str.contains(product_name, case=False, na=False)]

#         if product_data.empty:
#             dispatcher.utter_message(text="Xin lỗi, tôi không tìm thấy tính năng của sản phẩm này.")
#             return []
        
#         # Lấy tên đầy đủ của sản phẩm
#         full_product_name = product_data.iloc[0]['Tên sản phẩm']    
#         # Lấy tính năng sản phẩm
#         features = product_data.iloc[0]['Tính năng']
#         response = f"Tính năng của {full_product_name} là: {features}"

#         dispatcher.utter_message(text=response)
#         return []

# # Class to get the product link
# class ActionGetProductLink(Action):
#     def name(self) -> Text:
#         return "action_get_product_link"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # Lấy tên sản phẩm từ slot 'product'
#         product_name = tracker.get_slot("product")

#         # Kiểm tra nếu product_name là danh sách và lấy phần tử đầu tiên
#         if isinstance(product_name, list):
#             product_name = product_name[0]

#         # Tìm sản phẩm theo tên
#         product_data = df[df['Tên sản phẩm'].str.contains(product_name, case=False, na=False)]

#         if product_data.empty:
#             dispatcher.utter_message(text="Xin lỗi, tôi không tìm thấy link của sản phẩm này.")
#             return []
        
#         # Lấy tên đầy đủ của sản phẩm
#         full_product_name = product_data.iloc[0]['Tên sản phẩm']   

#         product_link = product_data.iloc[0]['Link sản phẩm']
#         dispatcher.utter_message(text=f"Đây là link của {full_product_name}: {product_link}")
#         return []
    
# # Class to get the product technical specifications
# class ActionGetProductTechnicalSpecs(Action):
#     def name(self) -> Text:
#         return "action_get_product_technical_specs"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # Lấy tên sản phẩm từ slot 'product'
#         product_name = tracker.get_slot("product")

#         # Kiểm tra nếu product_name là danh sách và lấy phần tử đầu tiên
#         if isinstance(product_name, list):
#             product_name = product_name[0]

#         # Tìm sản phẩm theo tên
#         product_data = df[df['Tên sản phẩm'].str.contains(product_name, case=False, na=False)]

#         if product_data.empty:
#             dispatcher.utter_message(text="Xin lỗi, tôi không tìm thấy thông số kỹ thuật của sản phẩm này.")
#             return []
        
#         # Lấy tên đầy đủ của sản phẩm
#         full_product_name = product_data.iloc[0]['Tên sản phẩm']   
#         technical_specs = product_data.iloc[0]['Thông số kỹ thuật']
#         dispatcher.utter_message(text=f"Thông số kỹ thuật của {full_product_name} là: {technical_specs}")
#         return [