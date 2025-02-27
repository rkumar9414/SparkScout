# RobotEvents API Configuration
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzIiwianRpIjoiOTU5MjY2Y2FkMjExM2Q0M2Y3NDQ3N2U4MWVhZmNkZDMzNDY2MmY1ZDg1MzljOTQzYTlmOWZhZWRjNjdkYTcwNjBiOWE4MzY4ZmU3MTAyM2MiLCJpYXQiOjE3NDA2MDc5ODEuNzkwNDI0MSwibmJmIjoxNzQwNjA3OTgxLjc5MDQyNiwiZXhwIjoyNjg3MjkyNzgxLjc4NTQzODEsInN1YiI6IjE0NDMzNiIsInNjb3BlcyI6W119.PY6W-dt4fffSVJC0HTdvIABHKE7Zob7XXlRplBWhimmd0wh52iNubTHPwp6flbtbqzwL6N-TI1at379hOp95XokenBklRg6qtRSdmZjex6peb2xCL7KLOcYh6DzVpr50O6w14QkzAFi6v9HYet723FyFI2k7P6_LG_EQiUIO-wjslRRx3yZoosSIXrKb2srsOc6Kr-KVQwEQgao1sURNABlRUdFx2o4teGJH-mToVW5T_O-VYIH692Q5Fb5C6AgxC4lJQMg0iEGyuvzsNRrTw1gNr7hooEWy-nMsJXFEV37sdQX5MiP7duR3iAHS46ttpMuI-dfjVTmcYxCqw8oZsTmahhyU0ePgo2s89hSdk03kPf7IKBvtWfjx1txtiiJaG49tSfUZqycE1Hi_RqeJ4JVjEAHB8qO6ujxk3MYkGe55u36nbeFbr7mA8s3f_OI-i0QLAO8SQsU1-rE2ubagSL4vbo6siRFqQL_H8rD8N_nD-4oJSW2OyonpTfL_UcK6pBLlWopdo-kcdyLNP3l6XPlQCh-Ff77kGmn0ePWgCLuJuxykpl8-cGXKNp3aJ2SQXjIPWTDlgaJN2aWtWhInptAEvEc-tRWdwk8kv9QApAL-PsSH47Dcn2uf_rTkxz_JuSbFNIkcZg9Myfgu4BM6n2cdD1mMnhmN3n9qgc7hnZY"  # Replace with your actual API key
BASE_URL = "https://www.robotevents.com/api/v2"

def get_headers():
    """
    Returns the headers required for RobotEvents API requests.
    Includes the API key for authentication.
    """
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }