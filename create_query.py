import os
import time
import google.generativeai as genai

# Configure the Google AI API
genai.configure(api_key='AIzaSyDRHjCNWC-diY_iQ3Zj90t5WS5GB2xuHBM')

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Function to generate issues
def generate_issues(num_issues=100):
    time.sleep(2)
    issues_data = ""
    for i in range(num_issues):
        # Retain the original history structure
        chat_session = model.start_chat(
            history=[
    {
      "role": "user",
      "parts": [
        "1. Theme Generation: Use an AI like ChatGPT or Claude to generate 50-100 common customer service themes for a neobank.\n2. Issue Scenario Generation: For each theme, generate 10 specific and diverse user issue scenarios. Specify whether the user is male or female as this might influence the type of query. This will result in 250-500 scenarios.\n3. Generate Typical Responses: For each scenario, generate an average or typical customer service response from a neobank like Jupiter.\n4. Extend the Conversation (Optional):  Pretend the user is in a very angry situation and further the conversation for at least four levels (user, chatbot, user, chatbot etc.).\n\n\n\nyou have to do this. tell me the your approach\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Here's a breakdown of my approach to tackle this challenge, incorporating best practices for generating realistic and helpful customer service scenarios:\n\n**1. Theme Generation**\n\n* **Utilize ChatGPT or Claude:** I'll leverage the capabilities of ChatGPT or Claude, providing them with specific instructions to generate customer service themes relevant to a neobank. \n    * **Prompt:** \"Generate 50-100 common customer service themes for a neobank, focusing on areas like account management, transactions, payments, security, mobile app issues, and customer support.\"\n    * **Refine:** I'll carefully review the generated themes, ensuring they cover a broad range of potential customer issues and are appropriate for a neobank context. \n* **Categorization:**  For better organization and analysis, I'll categorize the themes into logical groups (e.g., Account Management, Transactions, Security, Mobile App, Customer Support).\n\n**2. Issue Scenario Generation**\n\n* **Scenario Development:** For each theme, I'll use ChatGPT or Claude to create 10 diverse user issue scenarios. \n    * **Prompt Structure:** \n        * **Scenario Theme:**  \"Describe a scenario where a [male/female] customer is having trouble with [specific theme].\"\n        * **Specific Details:** \"Include details like the customer's age range, occupation, and any relevant context about their situation (e.g., traveling abroad, recent account changes).\"\n    * **Scenario Diversity:**  I'll ensure a mix of scenarios ranging from simple troubleshooting to complex issues, including:\n        * **Common Issues:**  Forgetting PIN, failed transaction, unexpected fees, account balance discrepancies.\n        * **Technical Issues:**  App crashes, account login problems, security alerts.\n        * **Frustrating Situations:**  Lost card, unauthorized transactions, delayed payments.\n* **Gender Considerations:** I'll specifically include the user's gender in the prompts to generate scenarios that are potentially influenced by gender-related experiences.\n\n**3. Typical Response Generation**\n\n* **Chatbot Persona:** I'll develop a consistent chatbot persona for the neobank (like Jupiter) based on its brand values and customer service style. This persona will guide the responses.\n* **Response Components:** Each response will include:\n    * **Acknowledgement:**  A friendly and empathetic acknowledgment of the user's problem.\n    * **Problem Identification:**  Clearly identifying the issue and clarifying any ambiguities.\n    * **Solution Suggestions:** Offering relevant and helpful solutions, including:\n        * **Troubleshooting Steps:**  For technical issues, clear and concise steps to resolve the problem.\n        * **Policy Explanation:**  For policy-related issues, providing clear explanations of relevant rules and procedures.\n        * **Escalation:**  If the issue requires further investigation or escalation to a human agent, explaining the process and next steps.\n    * **Call to Action:**  Inviting the user to respond or take specific action to move forward.\n\n**4. Extended Conversation (Optional)**\n\n* **Angry User Persona:** I'll create a persona for an angry user with specific needs and frustrations.\n* **Conversation Flow:** For each scenario, I'll simulate a conversation with the chatbot, iterating through four levels:\n    * **Level 1:**  User expresses frustration and explains the issue.\n    * **Level 2:**  Chatbot acknowledges the issue and attempts to resolve it.\n    * **Level 3:**  User escalates the situation, expressing further frustration and demanding a solution.\n    * **Level 4:**  Chatbot offers a more empathetic response, potentially offering a human agent escalation or a more decisive solution.\n\n**Important Considerations**\n\n* **Realism:**  The scenarios and responses should reflect real-world customer interactions and the limitations of AI-powered chatbots.\n* **Data Privacy:** I will be mindful of not generating scenarios that could potentially reveal sensitive customer information.\n* **Continuous Improvement:** I will use feedback from the generated scenarios and responses to refine the prompts and chatbot persona for greater accuracy and effectiveness.\n\nI hope this approach helps you create a valuable dataset for training and testing your customer service chatbot! \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "do #1\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "##Common Customer Service Themes for a Neobank\n\nHere are 100 common customer service themes for a neobank, categorized for better understanding:\n\n**Account Management**\n\n1. Account Setup & Verification\n2. Account Closure & Deactivation\n3. Account Limits & Restrictions\n4. Account Access & Login Issues\n5. Account Balance & Statement Inquiries\n6. Account Name & Contact Information Updates\n7. Account Transfer & Consolidation\n8. Account Security & Fraud Prevention\n9. Account Freezing & Unfreezing\n10. Account Linking & Integration (with other services)\n\n**Transactions**\n\n11. Domestic & International Transfers\n12. Bill Payments & Recurring Payments\n13. Mobile & Online Payments\n14. Transaction History & Reconciliation\n15. Transaction Limits & Approvals\n16. Transaction Fees & Charges\n17. Transaction Disputes & Refunds\n18. Failed Transactions & Error Resolution\n19. Transaction Tracking & Notifications\n20. Transaction Security & Authentication\n\n**Cards & Payments**\n\n21. Card Ordering & Delivery\n22. Card Activation & Setup\n23. Card Blocking & Unblocking\n24. Card Replacement & Lost/Stolen Card Reporting\n25. Card PIN & Security Settings\n26. Card Usage Limits & Restrictions\n27. Card Payment Options (e.g., contactless, tap & go)\n28. Card Transaction History & Statements\n29. Card Disputes & Chargebacks\n30. Card Security & Fraud Prevention\n\n**Investments & Savings**\n\n31. Investment Account Setup & Funding\n32. Investment Options & Portfolios\n33. Investment Performance & Reporting\n34. Investment Withdrawal & Redemption\n35. Investment Goals & Strategies\n36. Savings Account Interest Rates & Terms\n37. Savings Account Deposits & Withdrawals\n38. Savings Account Transfers & Consolidations\n39. Savings Account Goals & Budgeting Tools\n40. Savings Account Security & FDIC Insurance\n\n**Mobile App & Website**\n\n41. App Download & Installation\n42. App Login & Account Access\n43. App Navigation & User Interface\n44. App Features & Functionality (e.g., payments, transfers, budgeting tools)\n45. App Notifications & Alerts\n46. App Security & Data Privacy\n47. Website Navigation & Information\n48. Website Security & SSL Certificates\n49. Website Account Management Features\n50. Website Accessibility & Usability\n\n**Customer Support & Service**\n\n51. Contact Information & Availability\n52. Chat Support & Live Agent Availability\n53. Email Support & Response Times\n54. Phone Support & Call Center Operations\n55. Customer Service FAQs & Resources\n56. Complaints & Feedback Management\n57. Account Support & Troubleshooting\n58. Security & Fraud Support\n59. Technical Support & System Issues\n60. Customer Education & Financial Literacy\n\n**Security & Privacy**\n\n61. Account Security & Login Verification\n62. Two-Factor Authentication (2FA)\n63. Biometric Authentication & Fingerprint Recognition\n64. Security Alerts & Notifications\n65. Data Privacy & GDPR Compliance\n66. Fraud Prevention & Detection\n67. Security Settings & Preferences\n68. Phishing & Scam Awareness\n69. Data Encryption & Secure Transmission\n70. Account Recovery & Password Reset\n\n**Fees & Charges**\n\n71. Transaction Fees & Charges\n72. Account Maintenance Fees\n73. Overdraft Fees & Charges\n74. International Transaction Fees\n75. Currency Conversion Fees\n76. ATM Withdrawal Fees\n77. Late Payment Fees\n78. Account Inactivity Fees\n79. Fee Transparency & Disclosure\n80. Fee Waiver & Promotions\n\n**Loans & Credit**\n\n81. Personal Loan Application & Approval\n82. Loan Repayment & Amortization\n83. Loan Interest Rates & Terms\n84. Loan Eligibility & Requirements\n85. Loan Security & Collateral\n86. Loan Payment Options & Schedule\n87. Loan Prepayment & Refinancing\n88. Credit Score & Credit Reporting\n89. Credit Limit & Line of Credit\n90. Credit Card Rewards & Benefits\n\n**Financial Planning & Budgeting**\n\n91. Budgeting Tools & Resources\n92. Financial Goals & Planning\n93. Savings & Investment Advice\n94. Retirement Planning & Investments\n95. Financial Education & Courses\n96. Expense Tracking & Analysis\n97. Money Management Tips & Strategies\n98. Debt Management & Consolidation\n99. Financial Analysis & Reporting\n100. Personalized Financial Recommendations\n\nRemember, this is a starting point. You can further refine and expand on these themes based on your specific neobank's offerings and target audience. \n",
      ],
    },
  ]
        )

        # Send message and capture the response
        response = chat_session.send_message(f"""pick {i} issue from above and generate one diverse user issue. specify male or female. generate an average or typical customer service response from a neobank like Jupiter.Pretend the user is in a very angry situation and further the conversation for at least four levels (user, chatbot, user, chatbot etc.). Keep this format : heading with details, then messages with <username>:  then in new line chatbot. Make sure the data is upto the level where issue was resloved.
                                             
                                             return the response as csv format. send back only full response for one ticket only. make sure the customer act like in typical indian ways and also show some uncommon issues and non obvious issues. Pick a random unique issue from the above list. 


                                             
                                             issue,User,Response
1,"What the hell is going on? I just tried to send money to my friend in the UK, and it says the transaction failed! This is an emergency, and now I'm stuck! Why isn't this working?","I understand your frustration, [User Name]. Let's see what happened with the transaction. Could you please tell me the amount you tried to transfer and the recipient's details?"
1,"It's £500 to [Friend's Name] - [Friend's Account Number]! I can't believe this is happening! I need this money to get to my friend ASAP!","Thank you for that information. I've checked the system, and it seems the transaction was declined due to insufficient funds in your account. We will need to verify the balance before we can process the transfer. Could you confirm the current balance you are seeing in your account?"
1,"Insufficient funds? Are you kidding me? I have more than enough money! I just checked my account, and there's plenty in there! This is ridiculous! What's going on with your system?","I understand your frustration. It appears there might be a temporary glitch in our system causing the balance to be displayed incorrectly. Let me escalate this issue to a human agent who can review your account and the transaction details further. Please hold while I connect you."
1,"Finally, someone who can actually help! I need this sorted out now. This is an emergency.","Good afternoon, [User Name]. My name is [Agent Name]. I understand you're experiencing an issue with an international transfer. I've reviewed your account details and confirmed there are sufficient funds for the transfer. It seems the transaction was stuck due to a temporary system error. I have manually processed the transfer, and it should be completed within the next hour. I apologize for the inconvenience and appreciate your patience."
1,"Thank you, that's a relief. I hope this doesn't happen again. I need to be able to rely on your service, especially in emergencies.","I understand. We are working on improving our system's reliability to prevent these situations in the future. Please let me know if you have any other questions or concerns. Have a good day."
1,"Thank you.",""

                                             
                                             Current issue number is {i+1}. Make sure you use indian names and incorporate indian langauge ascent. the english should not be very fluent. BUt Dont use hindi langauge. The issue faced by users should be complex and customer should be showing high emotional flow. Make sure the csv structure is maintained properly. and the issue is uniquly picked from one of the above mentioned Common Customer Service Themes for a Neobank. Since We're using \" for values, make sure they dont appear in messages as they affect the csv format and make it non usuable. Also make sure customer is showing immense emotions and even threats sometimes. IMPORTANT  : MAKE SURE CSV FORMAT IS CORRECT, IT SHOULD FOLLOW ALL CSVLINT RULES.
                                             """,)

        # Formatting each issue and adding separators
        issues_data = response.text.replace('csv', '').replace('', '')
        print(i +1)
        with open("customer_service_issues04.csv", "+a", encoding='utf-8') as file:
          file.write(issues_data)

    # Write the issues to a file
    

# Generate 100 issues and save to a file
generate_issues(50)