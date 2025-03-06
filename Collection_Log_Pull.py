import os
import time
import datetime
import asyncio
import aiohttp

output_list_limit = 99 # Can be set to limit the total listed players (eg. 10 will only output top 10)
names_file_name = "cloggers.txt"
output_file_name = "clog_results.txt"

# Gets current date and returns in format DD/MM/YYYY
def get_current_date_string():
    return datetime.date.today().strftime("%d/%m/%Y")

# Outputs a minimum of 1 tab, adding 1 for every 4 rsn and rank characters combined less than the longest name
def return_tab_imputs(rsn, rank, rsns):
    max_tabs = 0
    for n in rsns:
        if round(len(n) / 4) > max_tabs:
            max_tabs = round(len(n) / 4)
    output_length = len(rsn) + len(str(rank))
    number_of_tabs = max_tabs - round(output_length / 4) + 1
    # print(f"{output_length} : {number_of_tabs}")
    return "\t" * number_of_tabs

# Define function to submit and retrieve API response
async def fetch_data(session, url, rsn):
    retries = 0
    max_retries = 5  # Set a maximum number of retries
    while retries < max_retries:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return rsn, await response.json()
                elif response.status == 503:
                    retries += 1
                    wait_time = 1 ** retries  # Exponential backoff
                    time.sleep(wait_time)  # Wait before retrying
                    print(f"Error ({response.status}): Server busy; Retrying for {rsn} (Attempt {retries}/{max_retries})")
                else:
                    print(f"Error ({response.status}) fetching {rsn} from official leaderboards: Wrong name or not ranked")
                    return rsn, None
        except aiohttp.ClientError as e:
            print(f"Client error fetching {rsn} from {url}: {e}")
            return rsn, None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return rsn, None

# Returns result of API response in a dictionary format
async def process_requests(api_urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url, rsn) for url, rsn in api_urls]
        results = await asyncio.gather(*tasks)
        return {rsn: data for rsn, data in results if data}

async def main():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    cloggers = []
    #Get names from file for processing
    with open(os.path.join(script_directory, names_file_name), "r") as file:
        rsns = [line.strip() for line in file]
        # print(rsns)

    # Set API urls with player names
    api_urls = [(f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.json?player={rsn}", rsn) for rsn in rsns]

    matched_data = await process_requests(api_urls)

    # Pull official Collection Log info and split into RSN and Clogs obtained
    for rsn, data in matched_data.items():
        cloggers.append({
            "name": rsn,
            "uniqueObtained": data["activities"][18]["score"]
        })

    # Sort from highest collections obtained to lowest
    sorted_data = sorted(cloggers, key=lambda x: x.get("uniqueObtained", 0), reverse=True) #Handle potential missing uniqueObtained

    # Format string for output. 
    output_string = f"Last updated {get_current_date_string()}\n\n"
    output_string_unranked = "\nThe following are not ranked on the official highscores:\n"
    for i, data in enumerate(sorted_data):
        obtained = data.get("uniqueObtained")
        if obtained != -1:
            output_string += f"Rank {i+1} - {data['name']}: {return_tab_imputs(data['name'], i, rsns)}{obtained}\n---\n"
        else:
            output_string_unranked += f" - {data['name']}\n"
        if i == output_list_limit:
            break
    # Combine output strings
    output_string += output_string_unranked

    # Write formated string to text file
    with open(os.path.join(script_directory, output_file_name), "w") as file:
        file.write(output_string)
        print("File output completed")
    # print(output_string)

if __name__ == "__main__":
    asyncio.run(main())
    input("Press Enter to close...") # Keeps window open to show any potential error messages