import requests 
import json
import dateutil.parser

secrets = json.load(open("secrets.json"))
github_token, repo_url, username, academic_year = \
    secrets["github_token"], secrets["repo_url"], secrets["username"], secrets["academic_year"],
headers = {'Authorization': 'token {}'.format(github_token)}

# Get Submitted Issues, Submitted PRs and Merged PRs
issues = []
prs = []

page_num = 1
should_terminate = False
while True: 
    dest_url = "{}/issues?creator={}&state=all&page={}".format(repo_url, username, page_num)
    data = requests.get(dest_url, headers=headers)
    json_data = json.loads(data.content)

    if len(json_data) == 0 or should_terminate:
        print("Issues done.")
        break 

    for json_doc in json_data:
        if not "pull_request" in json_doc: 
            created_at, title, number, url = json_doc["created_at"], \
                json_doc["title"], json_doc["number"], json_doc["html_url"]
            created_date = dateutil.parser.isoparse(created_at).strftime("%d %b %Y")
            created_date = dateutil.parser.isoparse(created_at)
            if created_date <= dateutil.parser.isoparse('{}-05-01T00:00:00.000000Z'.format(academic_year)):
                should_terminate = True
                break 

            created_date = created_date.strftime("%d %b %Y")

            res_str = "| {} | Submitted Issue: [{} #{}]({}) |".format(created_date, title.strip(), number, url)
            issues.append(res_str)
        else: 
            created_at, title, number, url = json_doc["created_at"], \
                json_doc["title"], json_doc["number"], json_doc["html_url"]
            created_date = dateutil.parser.isoparse(created_at)
            if created_date <= dateutil.parser.isoparse('{}-05-01T00:00:00.000000Z'.format(academic_year)):
                should_terminate = True
                break 

            created_date = created_date.strftime("%d %b %Y")

            res_str = "| {} | Submitted PR: [{} #{}]({}) |".format(created_date, title.strip(), number, url)
            prs.append(res_str)

            merged_at = json_doc["pull_request"]["merged_at"]
            if not merged_at is None: 
                merged_date = dateutil.parser.isoparse(merged_at).strftime("%d %b %Y")
                res_str = "| {} | Merged PR: [{} #{}]({}) |".format(merged_date, title.strip(), number, url)
                prs.append(res_str)   

    print("Page {} of issues done.".format(page_num))
    page_num = page_num + 1

# Get Reviewed PRs 
reviews = []

page_num = 1
should_terminate = False
while True: 
    dest_url = "{}/pulls?state=all&page={}".format(repo_url, page_num)
    data = requests.get(dest_url, headers=headers)
    json_data = json.loads(data.content)

    if len(json_data) == 0 or should_terminate:
        print("PRs done.")
        break 

    for json_doc in json_data:
        created_at, title, number, url = json_doc["created_at"], \
            json_doc["title"], json_doc["number"], json_doc["html_url"]
        created_date = dateutil.parser.isoparse(created_at) 
        if created_date <= dateutil.parser.isoparse('{}-05-01T00:00:00.000000Z'.format(academic_year)):
            should_terminate = True
            break 

        reviews_url = "{}/pulls/{}/reviews".format(repo_url, number)
        reviews_data = requests.get(reviews_url, headers=headers)
        reviews_data = json.loads(reviews_data.content)

        for review_doc in reviews_data:
            if review_doc["user"]["login"] == username: 
                review_date = review_doc["submitted_at"]
                review_date = dateutil.parser.isoparse(review_date).strftime("%d %b %Y")
                res_str = "| {} | Reviewed PR: [{} #{}]({}) |".format(review_date, title.strip(), number, url)
                reviews.append(res_str)   
                break 

    print("Page {} of PRs done.".format(page_num))
    page_num = page_num + 1
        
with open("progress.md", "w+") as f:
    f.write("### Issues\n\n| Week | Achievements |")
    for issue in issues:
        f.write(issue + "\n")
    f.write("\n")

    f.write("### Pull Requests\n\n| Week | Achievements |")
    for pr in prs:
        f.write(pr + "\n")
    f.write("\n")

    f.write("### PR Reviews\n\n| Week | Achievements |")
    for review in reviews:
        f.write(review + "\n")
    f.write("\n")
