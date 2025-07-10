from litellm import acompletion
import json
from math import ceil

SYSTEM_INSTRUCTIONS = """
You are a JSON formatter who is an expert in writing syntactically valid JSON.

Follow the rules and schema defined by the user and simply output the JSON as requested.
"""


async def structure_json_data(search_results):

    # Clean up unwanted keys
    for result in search_results:
        for key in [
            "thumbnails",
            "product_token",
            "serpapi_bing_product_api",
            "old_price",
            "free_shipping",
        ]:
            result.pop(key, None)

    final_results = []
    try:
        batch_size = 10
        total_batches = ceil(len(search_results) / batch_size)

        for i in range(total_batches):
            batch = search_results[i * batch_size : (i + 1) * batch_size]
            messages = [
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {
                    "role": "user",
                    "content": f"""
                        {batch}
                        
                        Conform this to the following format:

                        [
                            {{
                                "link":"https://apple.in//...",
                                "price":"999",
                                "currency":"USD",
                                "productName":"Apple iPhone 16 Pro",
                                "seller": "Name of seller like ebay or walmart etc",
                                "otherDetails": {{
                                    "key": "value"   
                                }}
                            }}
                        ]
                        
                        All keys must be in camelCase. Only include product-specific details in otherDetails such as size, color etc. In the productName, let there only be the product name and remove all the descriptions.
                        Use external_link as link. All fields are string datatypes.
                    """,
                },
            ]

            res = await acompletion(
                model="mistral/mistral-small-latest", messages=messages
            )
            content = (
                res.choices[0].message.content.replace("```json", "").replace("```", "")
            )
            dict_obj = json.loads(content)
            final_results.extend(dict_obj)

        return final_results

    except Exception as e:
        print(f"Error during LLM structuring: {str(e)}")
        return {
            "status": "error",
            "message": f"Error occurred during LLM structuring - {str(e)}",
        }
