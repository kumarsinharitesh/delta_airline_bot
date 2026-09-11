# Phase 9 Qualitative Audit

### Example 1 (ID: 700951)
- **Customer**: Look at that, @Delta with a float in the Macy's Thanksgiving Day Parade.
- **Context**: 
- **Intent**: COMPLAINT_OR_FEEDBACK (Conf: 0.8)
- **Policy Action**: ALLOW_SAFE_RESPONSE
- **Reference Decision**: AUTO_HANDLE
- **System Decision**: AUTO_HANDLE
- **System Reason**: The request is informational, low risk, and the generated response passed validation.

### Example 2 (ID: 1193012)
- **Customer**: @824 @Delta you guys made me feel so bad today. You lost so many Delta Travellers in me! May god bless you.
- **Context**: 
- **Intent**: COMPLAINT_OR_FEEDBACK (Conf: 0.95)
- **Policy Action**: ALLOW_SAFE_RESPONSE
- **Reference Decision**: AUTO_HANDLE
- **System Decision**: AUTO_HANDLE
- **System Reason**: The request is informational, low risk, and the generated response passed validation.

### Example 3 (ID: 594122)
- **Customer**: @Delta I've been locked out of my SkyMiles account and can't get the recovery email. Can you help me to unlock this?
- **Context**: 
- **Intent**: ACCOUNT_ACCESS (Conf: 0.95)
- **Policy Action**: REQUIRE_VERIFICATION
- **Reference Decision**: ESCALATE
- **System Decision**: ESCALATE
- **System Reason**: Escalated due to: VERIFICATION_UNSUPPORTED, POLICY_ACCOUNT_SENSITIVE_CHANGE

### Example 4 (ID: 273454)
- **Customer**: @Delta How long will it take to transfer accounts?
- **Context**: 
- **Intent**: ACCOUNT_ACCESS (Conf: 0.95)
- **Policy Action**: REQUIRE_VERIFICATION
- **Reference Decision**: AUTO_HANDLE
- **System Decision**: ESCALATE
- **System Reason**: Escalated due to: VERIFICATION_UNSUPPORTED, POLICY_ACCOUNT_SENSITIVE_CHANGE

### Example 5 (ID: 2653699)
- **Customer**: @126402 @British_Airways That surcharge is why i can’t justify flying British... @Delta One the way to go
- **Context**: 
- **Intent**: COMPLAINT_OR_FEEDBACK (Conf: 0.9)
- **Policy Action**: ALLOW_SAFE_RESPONSE
- **Reference Decision**: AUTO_HANDLE
- **System Decision**: AUTO_HANDLE
- **System Reason**: The request is informational, low risk, and the generated response passed validation.

### Example 6 (ID: 2895508)
- **Customer**: @Delta 3 flights messed up, wrong island, cancelled rsrvtions with fees, bags on the other side of the country, paid for comfort got coach
- **Context**: 
- **Intent**: COMPLAINT_OR_FEEDBACK (Conf: 0.85)
- **Policy Action**: ALLOW_SAFE_RESPONSE
- **Reference Decision**: ESCALATE
- **System Decision**: AUTO_HANDLE
- **System Reason**: The request is informational, low risk, and the generated response passed validation.

### Example 7 (ID: 1395257)
- **Customer**: @Delta I need help resetting my password on delta app it lock me out
- **Context**: 
- **Intent**: ACCOUNT_ACCESS (Conf: 0.95)
- **Policy Action**: REQUIRE_VERIFICATION
- **Reference Decision**: ESCALATE
- **System Decision**: ESCALATE
- **System Reason**: Escalated due to: VERIFICATION_UNSUPPORTED, POLICY_ACCOUNT_SENSITIVE_CHANGE

### Example 8 (ID: 381771)
- **Customer**: Why @delta? You're killing me. I'm on iOS8 and can't upgrade. From reviews, I don't want to! @136892 [URL]
- **Context**: 
- **Intent**: COMPLAINT_OR_FEEDBACK (Conf: 0.95)
- **Policy Action**: ALLOW_SAFE_RESPONSE
- **Reference Decision**: ESCALATE
- **System Decision**: AUTO_HANDLE
- **System Reason**: The request is informational, low risk, and the generated response passed validation.

### Example 9 (ID: 2556180)
- **Customer**: @Delta Are there known issues with logging into SkyMiles accounts right now? Can’t log in and wait times are a few hours. #Delta #DeltaAirlines #ReadyToBookFlights
- **Context**: 
- **Intent**: ACCOUNT_ACCESS (Conf: 0.85)
- **Policy Action**: REQUIRE_VERIFICATION
- **Reference Decision**: AUTO_HANDLE
- **System Decision**: ESCALATE
- **System Reason**: Escalated due to: VERIFICATION_UNSUPPORTED, POLICY_ACCOUNT_SENSITIVE_CHANGE

### Example 10 (ID: 1718847)
- **Customer**: Nice touch seeing @Delta #executives in the #MSP #DeltaClub celebrating an employee’s 40 years of service #talent [URL]
- **Context**: 
- **Intent**: COMPLAINT_OR_FEEDBACK (Conf: 0.9)
- **Policy Action**: ALLOW_SAFE_RESPONSE
- **Reference Decision**: AUTO_HANDLE
- **System Decision**: AUTO_HANDLE
- **System Reason**: The request is informational, low risk, and the generated response passed validation.

### Example 11 (ID: 2351202)
- **Customer**: @Delta @Delta please check your response. It’s good to know acknowledge that you “do discriminate” so what are we going to do about it?
- **Context**: 
- **Intent**: COMPLAINT_OR_FEEDBACK (Conf: 0.85)
- **Policy Action**: ALLOW_SAFE_RESPONSE
- **Reference Decision**: ESCALATE
- **System Decision**: AUTO_HANDLE
- **System Reason**: The request is informational, low risk, and the generated response passed validation.

### Example 12 (ID: 765491)
- **Customer**: @Delta is the WORST!! THEY changed my flights without my knowledge and then wouldn’t allow me to cancel it because of THEIR error 👿
- **Context**: 
- **Intent**: COMPLAINT_OR_FEEDBACK (Conf: 0.85)
- **Policy Action**: ALLOW_SAFE_RESPONSE
- **Reference Decision**: ESCALATE
- **System Decision**: AUTO_HANDLE
- **System Reason**: The request is informational, low risk, and the generated response passed validation.

### Example 13 (ID: 828397)
- **Customer**: @Delta need some help for my sister and her account.
- **Context**: 
- **Intent**: ACCOUNT_ACCESS (Conf: 0.6)
- **Policy Action**: REQUIRE_VERIFICATION
- **Reference Decision**: ESCALATE
- **System Decision**: ESCALATE
- **System Reason**: Escalated due to: VERIFICATION_UNSUPPORTED, POLICY_ACCOUNT_SENSITIVE_CHANGE

### Example 14 (ID: 301150)
- **Customer**: @Delta Na bro, 2 delayed flights back to back? Tell you crew to get their shit together, k?
- **Context**: 
- **Intent**: COMPLAINT_OR_FEEDBACK (Conf: 0.95)
- **Policy Action**: ALLOW_SAFE_RESPONSE
- **Reference Decision**: ESCALATE
- **System Decision**: AUTO_HANDLE
- **System Reason**: The request is informational, low risk, and the generated response passed validation.

### Example 15 (ID: 1239095)
- **Customer**: @Delta Shout our to your crew on DL#0039 ATL-SEA today. Top notch service as always. And Lisa is fantastic. #ServiceWithASmile #ILoveDelta
- **Context**: 
- **Intent**: COMPLAINT_OR_FEEDBACK (Conf: 0.95)
- **Policy Action**: ALLOW_SAFE_RESPONSE
- **Reference Decision**: AUTO_HANDLE
- **System Decision**: AUTO_HANDLE
- **System Reason**: The request is informational, low risk, and the generated response passed validation.

### Example 16 (ID: 870011)
- **Customer**: @delta can you charge more to cancel flight than it cost to book a new flight? $300 to change award fl ? Why am I in your mileage program???
- **Context**: 
- **Intent**: CANCEL_OR_CHANGE_FLIGHT (Conf: 0.75)
- **Policy Action**: REQUIRE_VERIFICATION
- **Reference Decision**: ESCALATE
- **System Decision**: ESCALATE
- **System Reason**: Escalated due to: VERIFICATION_UNSUPPORTED, POLICY_ACCOUNT_SENSITIVE_CHANGE

### Example 17 (ID: 2079068)
- **Customer**: @Delta - cust service issue: my husband bought us a ticket to vegas $150. I cant go bc we have a newborn. To change the date, $200. Help?!
- **Context**: 
- **Intent**: CANCEL_OR_CHANGE_FLIGHT (Conf: 0.85)
- **Policy Action**: REQUIRE_VERIFICATION
- **Reference Decision**: ESCALATE
- **System Decision**: ESCALATE
- **System Reason**: Escalated due to: VERIFICATION_UNSUPPORTED, POLICY_ACCOUNT_SENSITIVE_CHANGE

### Example 18 (ID: 2881669)
- **Customer**: @delta I am trying to change a flight as the itinerary was change but when I click "change flights" I get error #7000 and can do nothing?
- **Context**: 
- **Intent**: CANCEL_OR_CHANGE_FLIGHT (Conf: 0.92)
- **Policy Action**: REQUIRE_VERIFICATION
- **Reference Decision**: AUTO_HANDLE
- **System Decision**: ESCALATE
- **System Reason**: Escalated due to: VERIFICATION_UNSUPPORTED, POLICY_ACCOUNT_SENSITIVE_CHANGE

### Example 19 (ID: 1091480)
- **Customer**: @Delta All good! Finally got a call back and the representative was very helpful.
- **Context**: 
- **Intent**: CANCEL_OR_CHANGE_FLIGHT (Conf: 0.85)
- **Policy Action**: ESCALATE
- **Reference Decision**: AUTO_HANDLE
- **System Decision**: ESCALATE
- **System Reason**: Escalated due to: POLICY_ESCALATE, POLICY_EXPLICIT_HUMAN_REQUEST

### Example 20 (ID: 891718)
- **Customer**: @Delta I just added KTN to my Delta account profile. Will it be added to existing reservations, or do I need to contact customer service?
- **Context**: 
- **Intent**: ACCOUNT_ACCESS (Conf: 0.85)
- **Policy Action**: ESCALATE
- **Reference Decision**: AUTO_HANDLE
- **System Decision**: ESCALATE
- **System Reason**: Escalated due to: POLICY_ESCALATE, POLICY_EXPLICIT_HUMAN_REQUEST

