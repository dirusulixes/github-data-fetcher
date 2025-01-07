import csv
import json
import os

# Load CSV data into a dictionary
def load_csv(csv_file):
    affiliation_data = {}
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            affiliation_data[row['name']] = row['Company']
    return affiliation_data

# Add affiliation to JSON data and save to a new file
def add_affiliation_to_json(json_file, affiliation_data, new_json_file):
    if not os.path.exists(json_file):
        print(f"File {json_file} does not exist.")
        return

    with open(json_file, 'r') as file:
        data = json.load(file)

    modified = False
    for item in data:
        author = item.get('author')
        if author and author in affiliation_data:
            item['affiliation'] = affiliation_data[author]
            modified = True

    if modified:
        with open(new_json_file, 'w') as file:
            json.dump(data, file, indent=4)

# Main function
def main():
    csv_file = '/home/conaldi/git/github-data-fetcher/Istio Developers statistics.csv'
    affiliation_data = load_csv(csv_file)

    json_folder = '/home/conaldi/git/github-data-fetcher/'
    for filename in os.listdir(json_folder):
        if filename.endswith('.json'):
            json_file_path = os.path.join(json_folder, filename)
            new_json_file_path = os.path.join(json_folder, f'affiliated_{filename}')
            add_affiliation_to_json(json_file_path, affiliation_data, new_json_file_path)

if __name__ == "__main__":
    main()