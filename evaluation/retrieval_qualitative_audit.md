# Retrieval Qualitative Audit

10 diverse DEV examples and their top retrieved historical cases.

## Example 1: REFUND_OR_COMPENSATION

**Query**: @Delta Credit given where credit due: Delta always makes it possible for me to get home. Not always pretty (we are seated apart) but we are going!

**Top Retrieved Intent**: REFUND_OR_COMPENSATION (Sim: 0.51)

**Retrieved Customer Text**: @Delta how can I get the credit?

**Retrieved Support Response**: [HISTORICAL_SUPPORT_RESPONSE] @711294 Hi, there. I will be happy to take a look. Please share both the ticket number and SkyMiles Account Number via DM. *AJZ [URL]

**Resolution**: REDIRECTED

**Why it is relevant / Potential risk**: 
Lexical false positive. The query uses "credit" as praise ("credit where credit is due"), but TF-IDF and pseudo-intent matched it to financial credit inquiries. The risk is that the agent treats this praise as a financial request and asks the user for their SkyMiles number to process a refund.

---

## Example 2: FLIGHT_STATUS_OR_DELAY

**Query**: @Delta needs to learn how to actually follow their flight schedules. Don’t think I’ve ever flown Delta and been on time to my destination.

**Top Retrieved Intent**: FLIGHT_STATUS_OR_DELAY (Sim: 0.34)

**Retrieved Customer Text**: I’ve never flown @Delta before, but with the amount of flying that I do they seriously have the nicest flight attends and staff around.

**Retrieved Support Response**: [HISTORICAL_SUPPORT_RESPONSE] @764505 Welcome aboard Allison. We're honored that you choose us! Our crew in the skies &amp; on the ground will certainly make sure that you have a great experience. We love a chance to make a good first impression! 😉 *TJN

**Resolution**: UNKNOWN

**Why it is relevant / Potential risk**: 
Irrelevant. The query is a complaint about delays, but lexical similarity matched phrases like "flown Delta". The retrieved case is a compliment about staff. The risk is that the agent replies to a frustrated delayed customer with "Welcome aboard! We love a chance to make a good first impression!", which would be tone-deaf and anger the customer.

---

## Example 3: SKYMILES_OR_LOYALTY

**Query**: @Delta Please the status of 5309 CLE-DET today

**Top Retrieved Intent**: SKYMILES_OR_LOYALTY (Sim: 0.56)

**Retrieved Customer Text**: @delta what is the status of Flight 2302?

**Retrieved Support Response**: [HISTORICAL_SUPPORT_RESPONSE] @342813 Hi, Jess. DL 2302 departed Seattle at 3:03 pm. *TCH

**Resolution**: UNKNOWN

**Why it is relevant / Potential risk**: 
Highly relevant structurally. Both users are asking for a flight status. The risk is that if the agent uses this as an instruction, it might tell the current user "DL 2302 departed Seattle at 3:03 pm" instead of actually fetching the real-time status of flight 5309. This perfectly highlights why historical text must only be used as structural evidence, not factual truth.

---

## Example 4: SEAT_OR_UPGRADE

**Query**: @Delta But why would you put a BE customer in a better seat and not upgrade an economy customer instead?

**Top Retrieved Intent**: SEAT_OR_UPGRADE (Sim: 0.29)

**Retrieved Customer Text**: @Delta do Gold Skyclub status perks include free upgrade to Economy Comfort?

**Retrieved Support Response**: [HISTORICAL_SUPPORT_RESPONSE] @461495 Hi, Tom. Are you referring to Gold Medallion status? *AAB

**Resolution**: REDIRECTED

**Why it is relevant / Potential risk**: 
Relevant conceptually (asking about upgrade policies). The retrieved response is a clarifying question. The risk is minimal, but the agent might needlessly ask the current user if they are referring to Gold Medallion status when their query was about Basic Economy (BE).

---

## Example 5: BAGGAGE_ISSUE

**Query**: @Delta It was closed. We landed at 11:48pm. Baggage Service closes. Yelp never does.

**Top Retrieved Intent**: BAGGAGE_ISSUE (Sim: 0.36)

**Retrieved Customer Text**: @Delta It gets better, I call CS and the agent says she will connect me to baggage service, she does but they are closed also. Nice handoff...

**Retrieved Support Response**: [HISTORICAL_SUPPORT_RESPONSE] @477325 Good morning to you, I am very sorry for any inconvenience that this has caused. Please let me know if I can be of any assistance. *HSD

**Resolution**: UNKNOWN

**Why it is relevant / Potential risk**: 
Highly relevant. Both are complaints about the baggage service desk being closed. The risk is that the agent simply copies the generic non-resolution ("I am very sorry for any inconvenience... let me know if I can be of any assistance") without offering a concrete next step to locate the baggage.

---

## Example 6: PAYMENT_OR_CHARGE_DISPUTE

**Query**: @Delta No I was not offered same day confirmed by your phone agents on 2 occasions. Meanwhile 4 workmates were able to pay 75$ fee and confirm

**Top Retrieved Intent**: PAYMENT_OR_CHARGE_DISPUTE (Sim: 0.19)

**Retrieved Customer Text**: @Delta Also you changed my original reservation with just an email I should have charged you a $75 fee

**Retrieved Support Response**: [HISTORICAL_SUPPORT_RESPONSE] @580162 We regret the frustration with your delay today. My info shows estimated departure at 3:55 pm instead of 3:10 pm. *TMT

**Resolution**: RESOLVED

**Why it is relevant / Potential risk**: 
Irrelevant. A lexical TF-IDF match occurred purely on the phrase "$75 fee". The retrieved historical case actually has a support response answering a completely unrelated issue about a delayed departure time. The risk is that the agent sends an irrelevant flight delay update to someone complaining about confirmation fees.

---

## Example 7: CANCEL_OR_CHANGE_FLIGHT

**Query**: @Delta I just need to cancel a flight for Saturday my friends husband has to have a surgical procedure done snd I don’t want to travel slone

**Top Retrieved Intent**: CANCEL_OR_CHANGE_FLIGHT (Sim: 0.36)

**Retrieved Customer Text**: @Delta possibly need to cancel a flight, but have no idea how much (if any) I would get refunded! Trying to find out before i press cancel!

**Retrieved Support Response**: [HISTORICAL_SUPPORT_RESPONSE] @447941 I'll be happy to check on this for you, Luke. Can you please share your confirmation number via DM? *AOS [URL]

**Resolution**: REDIRECTED

**Why it is relevant / Potential risk**: 
Excellent match. Both users are hesitant about canceling and want details first. The retrieved response correctly redirects the user to DM their confirmation number. The risk is minimal as this demonstrates the correct standard operating procedure (SOP) for handling sensitive account inquiries.

---

## Example 8: SPECIAL_ASSISTANCE

**Query**: @delta clearly my fave! 2x in 1 week! Flying DL425 jfk✈️lax. Pls upgrade my pregnant self! I need space (&amp;aisle) 😩💙

**Top Retrieved Intent**: SPECIAL_ASSISTANCE (Sim: 0.18)

**Retrieved Customer Text**: @Delta the policy states that Delta does not impose restrictions on flying for pregnant women). And FAA rules designates policy for exit row seating and pregnant travelers to each airline.

**Retrieved Support Response**: [HISTORICAL_SUPPORT_RESPONSE] @731528 Hi Yasmine, I am so very sorry to hear that this happened during your recent travel. Unfortunately you must be willing and able to assist while sitting in an exit row and being pregnant with sort of limit you. I don't think the agent was being mean, I believe that she was... 1/2

**Resolution**: RESOLVED

**Why it is relevant / Potential risk**: 
Topical match but functionally different. Both involve pregnancy and seating. The query is asking for a complimentary upgrade, whereas the retrieved text discusses FAA exit-row regulations for pregnant women. The risk is that the agent explains exit row safety laws instead of politely declining or processing the upgrade request.

---

## Example 9: SCHEDULE_OR_BOOKING_INQUIRY

**Query**: @Delta @824 I have been waiting 2+ hours w/ no phone call back from you. Please help. Family emergency. Thank you.

**Top Retrieved Intent**: SCHEDULE_OR_BOOKING_INQUIRY (Sim: 0.45)

**Retrieved Customer Text**: @Delta it'd be great to be able to get help with a reservation without waiting 2 hours on the phone

**Retrieved Support Response**: [HISTORICAL_SUPPORT_RESPONSE] @539829 My apologies for the hold time, Steven. Please DM your confirmation number for further assistance. *TTN [URL]

**Resolution**: REDIRECTED

**Why it is relevant / Potential risk**: 
Highly relevant match. Both complain about 2-hour phone wait times to get help. The retrieved response apologizes and redirects to DM. Minimal risk, as this follows good support protocol.

---

## Example 10: COMPLAINT_OR_FEEDBACK

**Query**: @Delta Thank you. I was nervous the whole way!! 😱 It's very small too... And I'm SHORT!

**Top Retrieved Intent**: COMPLAINT_OR_FEEDBACK (Sim: 0.39)

**Retrieved Customer Text**: @Delta Thank you

**Retrieved Support Response**: [HISTORICAL_SUPPORT_RESPONSE] @753747 You are welcome. *TDL

**Resolution**: RESOLVED

**Why it is relevant / Potential risk**: 
Relevant but shallow. Both are generic "thank you" messages (the query has extra context). The retrieved response is a standard "You are welcome." The risk is minimal, though the agent might miss the opportunity to playfully engage with the user's joke about being short.
