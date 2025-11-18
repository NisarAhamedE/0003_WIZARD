--
-- PostgreSQL database dump
--

\restrict VzhLaa3io3lNSnsrZCysFCJYodqLewF4vvmHy1yUjxTy5sLln6aAYu6D9LTV6Xq

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: wizard_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.wizard_categories (id, name, description, icon, display_order, is_active, created_at, updated_at) FROM stdin;
8cd4dc3d-35cc-401e-bbce-a8208bae02f1	IT & Technology	Technology-related configuration wizards	computer	1	t	2025-11-17 22:15:11.211395+04	2025-11-17 22:15:11.211395+04
9182c947-fb40-4c28-8255-4f27d921b20f	Business Process	Business workflow and process wizards	business	2	t	2025-11-17 22:15:11.211395+04	2025-11-17 22:15:11.211395+04
404ac61d-5080-4619-8a75-0afbcbd93ade	Onboarding	User and employee onboarding wizards	person_add	3	t	2025-11-17 22:15:11.211395+04	2025-11-17 22:15:11.211395+04
3435f25f-a733-4c0c-b3e5-7ef970bbbc4d	Surveys & Forms	Data collection and feedback wizards	poll	5	t	2025-11-17 22:15:11.211395+04	2025-11-17 22:15:11.211395+04
53865cf8-584f-4e68-9c4a-6debd621d6f3	E-Commerce	Product configuration and shopping wizards	shopping_cart	4	t	2025-11-17 22:15:11.211395+04	2025-11-17 22:15:11.211395+04
\.


--
-- Data for Name: wizards; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.wizards (id, name, description, category_id, created_by, icon, cover_image, is_published, is_active, allow_templates, require_login, allow_anonymous, auto_save, auto_save_interval, estimated_time, difficulty_level, tags, total_sessions, completed_sessions, average_completion_time, created_at, updated_at, published_at) FROM stdin;
c5b66e5b-bcc8-4904-a60e-e17aa3a42e91	Wizard 1	Wizard 1	8cd4dc3d-35cc-401e-bbce-a8208bae02f1	511c6c86-347d-40d7-b946-1c689500c4a2	\N	\N	f	t	t	t	f	t	30	\N	easy	[]	0	0	\N	2025-11-17 18:40:18.026401+04	2025-11-17 18:40:18.026403+04	\N
6236eef9-f522-42ae-afcd-40709718a17a	Quick Feedback Survey	A simple survey to collect user feedback about our platform	3435f25f-a733-4c0c-b3e5-7ef970bbbc4d	511c6c86-347d-40d7-b946-1c689500c4a2	feedback	\N	t	t	t	f	f	t	30	3	easy	["survey", "feedback", "quick"]	4	0	\N	2025-11-17 22:15:11.220901+04	2025-11-17 18:45:52.191328+04	\N
11111111-1111-1111-1111-111111111111	Custom T-Shirt Designer	Design your perfect custom t-shirt with our step-by-step configurator. Choose size, color, material, print options, and more!	53865cf8-584f-4e68-9c4a-6debd621d6f3	511c6c86-347d-40d7-b946-1c689500c4a2	checkroom	\N	t	t	t	t	f	t	30	15	easy	["clothing", "t-shirt", "custom", "print"]	0	0	\N	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04	\N
22222222-2222-2222-2222-222222222222	Laptop Configuration Wizard	Build your perfect laptop by choosing processor, RAM, storage, display, and accessories. Get the exact specifications you need!	53865cf8-584f-4e68-9c4a-6debd621d6f3	511c6c86-347d-40d7-b946-1c689500c4a2	laptop	\N	t	t	t	t	f	t	30	20	medium	["electronics", "laptop", "computer", "custom-build"]	7	0	\N	2025-11-17 22:51:23.376103+04	2025-11-17 19:19:36.733812+04	\N
\.


--
-- Data for Name: steps; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.steps (id, wizard_id, name, description, help_text, step_order, is_required, is_skippable, allow_back_navigation, layout, custom_styles, validation_rules, created_at, updated_at) FROM stdin;
bde682c7-aa0f-496c-9f0d-2e070f1bc5e8	6236eef9-f522-42ae-afcd-40709718a17a	Overall Rating	How would you rate your overall experience?	Select the option that best describes your experience.	1	t	f	t	vertical	{}	{}	2025-11-17 22:15:11.224785+04	2025-11-17 22:15:11.224785+04
5d4e2fec-3feb-47dc-8a9c-d9e6364d512b	6236eef9-f522-42ae-afcd-40709718a17a	Features	Which features do you use most?	\N	2	t	f	t	vertical	{}	{}	2025-11-17 22:15:11.224785+04	2025-11-17 22:15:11.224785+04
30cc609f-16be-42c5-8503-2ee0882b9d10	6236eef9-f522-42ae-afcd-40709718a17a	Additional Comments	Any other feedback?	\N	3	f	t	t	vertical	{}	{}	2025-11-17 22:15:11.224785+04	2025-11-17 22:15:11.224785+04
95ffb6ce-efcd-4e0c-af76-1766faa0907f	c5b66e5b-bcc8-4904-a60e-e17aa3a42e91	License Type Selection	License Type Selection	License Type Selection	1	t	f	t	vertical	{}	{}	2025-11-17 18:40:18.028405+04	2025-11-17 18:40:18.028407+04
66b058ff-a05f-4b0d-b17e-88b786abc94f	c5b66e5b-bcc8-4904-a60e-e17aa3a42e91	Plan and Region Configuration	Plan and Region Configuration	Plan and Region Configuration	2	t	f	t	vertical	{}	{}	2025-11-17 18:40:18.032385+04	2025-11-17 18:40:18.032387+04
702253cc-4832-441a-bcc5-26e6d181b255	c5b66e5b-bcc8-4904-a60e-e17aa3a42e91	Billing Frequency	Billing Frequency	Billing Frequency	3	t	f	t	vertical	{}	{}	2025-11-17 18:40:18.034394+04	2025-11-17 18:40:18.034395+04
11111111-0001-0001-0001-111111111111	11111111-1111-1111-1111-111111111111	Select Your Size	Choose the t-shirt size that fits you best	Refer to our size chart if you are unsure about your measurements	1	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0002-0002-0002-111111111111	11111111-1111-1111-1111-111111111111	Choose Your Color	Pick your favorite t-shirt color	Popular colors include white, black, and navy blue	2	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0003-0003-0003-111111111111	11111111-1111-1111-1111-111111111111	Select Material	Choose the fabric type for comfort and durability	Cotton is breathable, polyester is moisture-wicking	3	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0004-0004-0004-111111111111	11111111-1111-1111-1111-111111111111	Print Locations	Select where you want your design printed	You can select multiple print locations	4	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0005-0005-0005-111111111111	11111111-1111-1111-1111-111111111111	Personalization	Add your custom text and preferences	Enter any text you want printed on your t-shirt	5	f	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0006-0006-0006-111111111111	11111111-1111-1111-1111-111111111111	Quantity & Checkout	Select quantity and additional services	Bulk orders over 10 items get 10% discount	6	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0001-0001-0001-222222222222	22222222-2222-2222-2222-222222222222	Choose Processor	Select the CPU that powers your laptop	Higher core count means better performance	1	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0002-0002-0002-222222222222	22222222-2222-2222-2222-222222222222	Select Memory (RAM)	Choose how much RAM you need	16GB is recommended for most users	2	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0003-0003-0003-222222222222	22222222-2222-2222-2222-222222222222	Storage Options	Configure your storage drives	NVMe SSDs offer fastest speeds	3	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0004-0004-0004-222222222222	22222222-2222-2222-2222-222222222222	Display Configuration	Choose your screen specifications	Higher resolution provides better visuals	4	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0005-0005-0005-222222222222	22222222-2222-2222-2222-222222222222	Software & Features	Select operating system and software	Choose the software bundle that fits your workflow	5	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-222222222222	22222222-2222-2222-2222-222222222222	Accessories & Warranty	Add accessories and warranty protection	Protect your investment with extended warranty	6	t	f	t	vertical	{}	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
\.


--
-- Data for Name: option_sets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.option_sets (id, step_id, name, description, selection_type, is_required, min_selections, max_selections, min_value, max_value, regex_pattern, custom_validation, display_order, placeholder, help_text, step_increment, created_at, updated_at) FROM stdin;
da602b64-48ec-40e2-9b25-bb8b6332b218	bde682c7-aa0f-496c-9f0d-2e070f1bc5e8	Experience Rating	Rate your experience from 1-5 stars	single_select	t	0	\N	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:15:11.230314+04	2025-11-17 22:15:11.230314+04
89642091-109c-4870-9429-7ff34ea5bc89	5d4e2fec-3feb-47dc-8a9c-d9e6364d512b	Most Used Features	Select all features you use regularly	multiple_select	t	1	5	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:15:11.230314+04	2025-11-17 22:15:11.230314+04
1d5379c6-de83-4bf3-b326-65bb166bd4ab	30cc609f-16be-42c5-8503-2ee0882b9d10	Your Comments	Share your thoughts with us	text_input	f	0	\N	\N	\N	\N	{}	1	Type your comments here...	\N	1	2025-11-17 22:15:11.230314+04	2025-11-17 22:15:11.230314+04
b17a80e3-3974-4492-998f-3ad5dfb080bf	95ffb6ce-efcd-4e0c-af76-1766faa0907f	New Option Set	\N	single_select	t	0	\N	\N	\N	\N	{}	0	\N	\N	1	2025-11-17 18:40:18.029832+04	2025-11-17 18:40:18.029833+04
7cd333c0-ce78-40a6-9990-8c3dec77bcbd	66b058ff-a05f-4b0d-b17e-88b786abc94f	Choose Your Plan	Choose Your Plan	single_select	t	0	\N	\N	\N	\N	{}	0	\N	\N	1	2025-11-17 18:40:18.033098+04	2025-11-17 18:40:18.033099+04
c8b7179b-b8b0-4a9e-b71e-738999faa634	702253cc-4832-441a-bcc5-26e6d181b255	New Option Set	\N	single_select	t	0	\N	\N	\N	\N	{}	0	\N	\N	1	2025-11-17 18:40:18.034913+04	2025-11-17 18:40:18.034914+04
11111111-0001-0001-0001-aaaaaaaaaaaa	11111111-0001-0001-0001-111111111111	T-Shirt Size	Select your preferred size	single_select	t	0	\N	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0002-0002-0002-aaaaaaaaaaaa	11111111-0002-0002-0002-111111111111	T-Shirt Color	Choose from our available colors	single_select	t	0	\N	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0003-0003-0003-aaaaaaaaaaaa	11111111-0003-0003-0003-111111111111	Fabric Material	Select your preferred material	single_select	t	0	\N	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0004-0004-0004-aaaaaaaaaaaa	11111111-0004-0004-0004-111111111111	Print Locations	Choose one or more print areas	multiple_select	t	1	4	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0005-0005-0005-aaaaaaaaaaaa	11111111-0005-0005-0005-111111111111	Custom Text	Enter text to be printed (max 50 characters)	text_input	f	0	\N	\N	\N	\N	{}	1	Enter your custom text here...	Text will be printed in the location you selected	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0005-0005-0005-bbbbbbbbbbbb	11111111-0005-0005-0005-111111111111	Design Importance	How important is the design quality to you? (1-5)	rating	f	0	\N	\N	\N	\N	{}	2	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0006-0006-0006-aaaaaaaaaaaa	11111111-0006-0006-0006-111111111111	Quantity	How many t-shirts do you want?	number_input	t	0	\N	1	100	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0006-0006-0006-bbbbbbbbbbbb	11111111-0006-0006-0006-111111111111	Additional Services	Select any additional services	multiple_select	f	0	\N	\N	\N	\N	{}	2	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0001-0001-0001-aaaaaaaaaaaa	22222222-0001-0001-0001-222222222222	Processor (CPU)	Choose your processor	single_select	t	0	\N	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0002-0002-0002-aaaaaaaaaaaa	22222222-0002-0002-0002-222222222222	RAM Capacity	Select memory size	single_select	t	0	\N	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0003-0003-0003-aaaaaaaaaaaa	22222222-0003-0003-0003-222222222222	Primary Storage	Main SSD drive	single_select	t	0	\N	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0004-0004-0004-aaaaaaaaaaaa	22222222-0004-0004-0004-222222222222	Display Type	Select screen specifications	single_select	t	0	\N	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0005-0005-0005-aaaaaaaaaaaa	22222222-0005-0005-0005-222222222222	Operating System	Pre-installed OS	single_select	t	0	\N	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0005-0005-0005-bbbbbbbbbbbb	22222222-0005-0005-0005-222222222222	Additional Software	Select software bundles	multiple_select	f	0	\N	\N	\N	\N	{}	2	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-aaaaaaaaaaaa	22222222-0006-0006-0006-222222222222	Warranty Plan	Extended warranty options	single_select	t	0	\N	\N	\N	\N	{}	1	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-bbbbbbbbbbbb	22222222-0006-0006-0006-222222222222	Accessories	Add useful accessories	multiple_select	f	0	\N	\N	\N	\N	{}	2	\N	\N	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-cccccccccccc	22222222-0006-0006-0006-222222222222	Special Instructions	Any special requests	text_input	f	0	\N	\N	\N	\N	{}	3	Enter any special instructions here...	We will do our best to accommodate	1	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
\.


--
-- Data for Name: options; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.options (id, option_set_id, label, value, description, display_order, icon, image_url, price, currency, is_default, is_recommended, is_active, metadata, created_at, updated_at) FROM stdin;
bd095b31-2488-4c2f-b59b-4a3cac216bb5	da602b64-48ec-40e2-9b25-bb8b6332b218	⭐ Poor	1	\N	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:15:11.233338+04	2025-11-17 22:15:11.233338+04
d4b428ee-a52d-43a2-ad38-1f8d5bc1f86b	da602b64-48ec-40e2-9b25-bb8b6332b218	⭐⭐ Fair	2	\N	2	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:15:11.233338+04	2025-11-17 22:15:11.233338+04
6995ca76-51b6-43b8-93e9-9c007fbd5ee1	da602b64-48ec-40e2-9b25-bb8b6332b218	⭐⭐⭐ Good	3	\N	3	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:15:11.233338+04	2025-11-17 22:15:11.233338+04
428a9543-3482-4b2b-b8a2-8a40b8166484	da602b64-48ec-40e2-9b25-bb8b6332b218	⭐⭐⭐⭐ Very Good	4	\N	4	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:15:11.233338+04	2025-11-17 22:15:11.233338+04
da5e2e27-e5d4-4221-86d4-a6b4cc1761f2	da602b64-48ec-40e2-9b25-bb8b6332b218	⭐⭐⭐⭐⭐ Excellent	5	\N	5	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:15:11.233338+04	2025-11-17 22:15:11.233338+04
eb00ac7d-6460-4c6c-be02-d40f5613791a	89642091-109c-4870-9429-7ff34ea5bc89	Wizard Builder	wizard_builder	\N	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:15:11.233338+04	2025-11-17 22:15:11.233338+04
0400e036-ff45-435d-a720-47a9134bce67	89642091-109c-4870-9429-7ff34ea5bc89	Session Management	session_mgmt	\N	2	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:15:11.233338+04	2025-11-17 22:15:11.233338+04
faaf0ec1-a1aa-4e50-844f-547f89e70bab	89642091-109c-4870-9429-7ff34ea5bc89	Templates	templates	\N	3	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:15:11.233338+04	2025-11-17 22:15:11.233338+04
f4f8e0c9-0c68-4e48-93c5-d1787de6428e	89642091-109c-4870-9429-7ff34ea5bc89	Analytics Dashboard	analytics	\N	4	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:15:11.233338+04	2025-11-17 22:15:11.233338+04
dfdfdf4b-34eb-430d-b31a-8b9de41ee984	89642091-109c-4870-9429-7ff34ea5bc89	User Management	user_mgmt	\N	5	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:15:11.233338+04	2025-11-17 22:15:11.233338+04
ce727e50-8233-488c-8b8a-4d803718eedb	b17a80e3-3974-4492-998f-3ad5dfb080bf	Personal 	Personal 	\N	0	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 18:40:18.031348+04	2025-11-17 18:40:18.031349+04
abe0f1fa-ef88-45af-93ee-7a8dd6b0e07a	b17a80e3-3974-4492-998f-3ad5dfb080bf	Business 	Business 	\N	0	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 18:40:18.031351+04	2025-11-17 18:40:18.031352+04
ac4d1ddf-3054-4133-9867-71d2c05381c3	b17a80e3-3974-4492-998f-3ad5dfb080bf	Enterprise 	Enterprise 	\N	0	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 18:40:18.031353+04	2025-11-17 18:40:18.031354+04
22dfb5d9-5550-4f26-97f3-e80799e4a3f3	7cd333c0-ce78-40a6-9990-8c3dec77bcbd	Team Plan	Team Plan	\N	0	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 18:40:18.033839+04	2025-11-17 18:40:18.03384+04
5dc48e37-c741-4c6f-a104-f041a08102f2	7cd333c0-ce78-40a6-9990-8c3dec77bcbd	Corporate 	Corporate 	\N	0	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 18:40:18.033843+04	2025-11-17 18:40:18.033844+04
91c0c07a-7383-436f-8ae0-f233a5a9a37e	c8b7179b-b8b0-4a9e-b71e-738999faa634	Monthly 	Monthly 	\N	0	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 18:40:18.03547+04	2025-11-17 18:40:18.035471+04
76d432b3-0ee4-4e4d-b5e8-dc011c59af42	c8b7179b-b8b0-4a9e-b71e-738999faa634	Annual 	Annual 	\N	0	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 18:40:18.035473+04	2025-11-17 18:40:18.035474+04
11111111-0001-0001-0001-000000000001	11111111-0001-0001-0001-aaaaaaaaaaaa	Small (S)	small	Chest: 34-36"	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0001-0001-0001-000000000002	11111111-0001-0001-0001-aaaaaaaaaaaa	Medium (M)	medium	Chest: 38-40"	2	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0001-0001-0001-000000000003	11111111-0001-0001-0001-aaaaaaaaaaaa	Large (L)	large	Chest: 42-44"	3	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0001-0001-0001-000000000004	11111111-0001-0001-0001-aaaaaaaaaaaa	X-Large (XL)	xlarge	Chest: 46-48"	4	\N	\N	2.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0001-0001-0001-000000000005	11111111-0001-0001-0001-aaaaaaaaaaaa	XX-Large (XXL)	xxlarge	Chest: 50-52"	5	\N	\N	4.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0002-0002-0002-000000000001	11111111-0002-0002-0002-aaaaaaaaaaaa	White	white	Classic white	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0002-0002-0002-000000000002	11111111-0002-0002-0002-aaaaaaaaaaaa	Black	black	Solid black	2	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0002-0002-0002-000000000003	11111111-0002-0002-0002-aaaaaaaaaaaa	Navy Blue	navy	Deep navy blue	3	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0002-0002-0002-000000000004	11111111-0002-0002-0002-aaaaaaaaaaaa	Red	red	Vibrant red	4	\N	\N	1.50	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0002-0002-0002-000000000005	11111111-0002-0002-0002-aaaaaaaaaaaa	Forest Green	green	Natural forest green	5	\N	\N	1.50	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0003-0003-0003-000000000001	11111111-0003-0003-0003-aaaaaaaaaaaa	100% Cotton	cotton	Natural, breathable, soft	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0003-0003-0003-000000000002	11111111-0003-0003-0003-aaaaaaaaaaaa	Polyester Blend	polyester_blend	60% Cotton, 40% Polyester	2	\N	\N	3.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0003-0003-0003-000000000003	11111111-0003-0003-0003-aaaaaaaaaaaa	Tri-Blend	tri_blend	50% Poly, 25% Cotton, 25% Rayon	3	\N	\N	5.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0003-0003-0003-000000000004	11111111-0003-0003-0003-aaaaaaaaaaaa	Organic Cotton	organic	100% certified organic	4	\N	\N	8.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0004-0004-0004-000000000001	11111111-0004-0004-0004-aaaaaaaaaaaa	Front Center	front_center	Large print on front chest	1	\N	\N	10.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0004-0004-0004-000000000002	11111111-0004-0004-0004-aaaaaaaaaaaa	Back Full	back_full	Full back print	2	\N	\N	12.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0004-0004-0004-000000000003	11111111-0004-0004-0004-aaaaaaaaaaaa	Left Sleeve	left_sleeve	Small print on left sleeve	3	\N	\N	5.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0004-0004-0004-000000000004	11111111-0004-0004-0004-aaaaaaaaaaaa	Right Sleeve	right_sleeve	Small print on right sleeve	4	\N	\N	5.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0006-0006-0006-000000000001	11111111-0006-0006-0006-bbbbbbbbbbbb	Gift Wrapping	gift_wrap	Premium gift wrapping	1	\N	\N	5.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0006-0006-0006-000000000002	11111111-0006-0006-0006-bbbbbbbbbbbb	Express Shipping	express_ship	2-day express delivery	2	\N	\N	15.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
11111111-0006-0006-0006-000000000003	11111111-0006-0006-0006-bbbbbbbbbbbb	Design Proof	design_proof	Email proof before printing	3	\N	\N	3.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0001-0001-0001-000000000001	22222222-0001-0001-0001-aaaaaaaaaaaa	Intel Core i5-13400	i5_13400	10 cores, up to 4.6GHz	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0001-0001-0001-000000000002	22222222-0001-0001-0001-aaaaaaaaaaaa	Intel Core i7-13700	i7_13700	16 cores, up to 5.2GHz	2	\N	\N	150.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0001-0001-0001-000000000003	22222222-0001-0001-0001-aaaaaaaaaaaa	Intel Core i9-13900	i9_13900	24 cores, up to 5.8GHz	3	\N	\N	350.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0001-0001-0001-000000000004	22222222-0001-0001-0001-aaaaaaaaaaaa	AMD Ryzen 7 7800X	ryzen7_7800x	8 cores, up to 5.0GHz	4	\N	\N	120.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0002-0002-0002-000000000001	22222222-0002-0002-0002-aaaaaaaaaaaa	8GB DDR5	8gb	Basic usage	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0002-0002-0002-000000000002	22222222-0002-0002-0002-aaaaaaaaaaaa	16GB DDR5	16gb	Recommended	2	\N	\N	80.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0002-0002-0002-000000000003	22222222-0002-0002-0002-aaaaaaaaaaaa	32GB DDR5	32gb	Professional	3	\N	\N	180.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0002-0002-0002-000000000004	22222222-0002-0002-0002-aaaaaaaaaaaa	64GB DDR5	64gb	Extreme	4	\N	\N	400.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0003-0003-0003-000000000001	22222222-0003-0003-0003-aaaaaaaaaaaa	256GB NVMe SSD	256gb_nvme	Basic storage	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0003-0003-0003-000000000002	22222222-0003-0003-0003-aaaaaaaaaaaa	512GB NVMe SSD	512gb_nvme	Standard storage	2	\N	\N	60.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0003-0003-0003-000000000003	22222222-0003-0003-0003-aaaaaaaaaaaa	1TB NVMe SSD	1tb_nvme	Ample storage	3	\N	\N	120.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0003-0003-0003-000000000004	22222222-0003-0003-0003-aaaaaaaaaaaa	2TB NVMe SSD	2tb_nvme	Plenty of space	4	\N	\N	250.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0004-0004-0004-000000000001	22222222-0004-0004-0004-aaaaaaaaaaaa	15.6" FHD 60Hz	15_fhd_60	1920x1080, standard	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0004-0004-0004-000000000002	22222222-0004-0004-0004-aaaaaaaaaaaa	15.6" FHD 144Hz	15_fhd_144	1920x1080, smooth	2	\N	\N	100.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0004-0004-0004-000000000003	22222222-0004-0004-0004-aaaaaaaaaaaa	15.6" QHD 165Hz	15_qhd_165	2560x1440, crisp	3	\N	\N	200.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0004-0004-0004-000000000004	22222222-0004-0004-0004-aaaaaaaaaaaa	16" 4K OLED	16_4k_oled	3840x2160, stunning	4	\N	\N	450.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0005-0005-0005-000000000001	22222222-0005-0005-0005-aaaaaaaaaaaa	Windows 11 Home	win11_home	Standard Windows	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0005-0005-0005-000000000002	22222222-0005-0005-0005-aaaaaaaaaaaa	Windows 11 Pro	win11_pro	Advanced features	2	\N	\N	50.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0005-0005-0005-000000000003	22222222-0005-0005-0005-aaaaaaaaaaaa	Ubuntu Linux	ubuntu	Free open-source OS	3	\N	\N	-20.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0005-0005-0005-000000000004	22222222-0005-0005-0005-bbbbbbbbbbbb	Microsoft Office 365	office365	Word, Excel, PowerPoint	1	\N	\N	99.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0005-0005-0005-000000000005	22222222-0005-0005-0005-bbbbbbbbbbbb	Adobe Creative Suite	adobe_cc	Photoshop, Illustrator	2	\N	\N	299.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0005-0005-0005-000000000006	22222222-0005-0005-0005-bbbbbbbbbbbb	Antivirus Pro (3yr)	antivirus	Security protection	3	\N	\N	79.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-000000000001	22222222-0006-0006-0006-aaaaaaaaaaaa	Standard 1 Year	warranty_1yr	Basic warranty	1	\N	\N	0.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-000000000002	22222222-0006-0006-0006-aaaaaaaaaaaa	Extended 2 Years	warranty_2yr	Extra year	2	\N	\N	99.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-000000000003	22222222-0006-0006-0006-aaaaaaaaaaaa	Premium 3 Years	warranty_3yr	Full 3-year	3	\N	\N	179.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-000000000004	22222222-0006-0006-0006-bbbbbbbbbbbb	Laptop Bag	laptop_bag	Premium carrying case	1	\N	\N	49.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-000000000005	22222222-0006-0006-0006-bbbbbbbbbbbb	Wireless Mouse	wireless_mouse	Ergonomic mouse	2	\N	\N	29.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-000000000006	22222222-0006-0006-0006-bbbbbbbbbbbb	USB-C Hub	usbc_hub	7-in-1 docking station	3	\N	\N	79.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
22222222-0006-0006-0006-000000000007	22222222-0006-0006-0006-bbbbbbbbbbbb	Laptop Stand	laptop_stand	Ergonomic stand	4	\N	\N	59.00	USD	f	f	t	{}	2025-11-17 22:51:23.376103+04	2025-11-17 22:51:23.376103+04
\.


--
-- PostgreSQL database dump complete
--

\unrestrict VzhLaa3io3lNSnsrZCysFCJYodqLewF4vvmHy1yUjxTy5sLln6aAYu6D9LTV6Xq

