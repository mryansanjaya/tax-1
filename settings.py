from os import environ

SESSION_CONFIGS = [
    dict(
        name='compound_kecil',
        app_sequence=['intro','compound_practice_kecil','compound_kecil'],
        num_demo_participants=2,
    ),
    dict(
        name='compound_kecil_random',
        app_sequence=['intro','compound_practice_random_kecil','compound_kecil'],
        num_demo_participants=2,
    ),
    dict(
        name='compound_sedang',
        app_sequence=['intro', 'compound_practice_sedang', 'compound_kecil'],
        num_demo_participants=2,
    ),
    dict(
        name='compound_sedang_random',
        app_sequence=['intro', 'compound_practice_random_sedang', 'compound_kecil'],
        num_demo_participants=2,
    ),
    dict(
        name='compound_besar',
        app_sequence=['intro', 'compound_practice_besar', 'compound_kecil'],
        num_demo_participants=2,
    ),
    dict(
        name='compound_besar_random',
        app_sequence=['intro', 'compound_practice_random_besar', 'compound_kecil'],
        num_demo_participants=2,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

SESSION_FIELDS = [
    'completions_by_treatment',
    'past_groups',
    'matrices',
    'wait_for_ids',
    'arrived_ids',
]

PARTICIPANT_FIELDS = [
    'app_payoffs',
    'app_row',
    'expiry',
    'finished_rounds',
    'language',
    'num_rounds',
    'partner_history',
    'past_group_id',
    'progress',
    'quiz_num_correct',
    'selected_round',
    'task_rounds',
    'time_pressure',
    'wait_page_arrival',
    'umr_list',
    'iw_lists',
    'sw_lists',
    'endowment_lists',
    'iw_type',
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'Rp'
USE_POINTS = False

# Rooms
ROOMS = [
    dict(
        name="eksperimenB1",
        display_name="eksperimen lab B",
        participant_label_file='_rooms/participant_labelsB_sesi1.txt',
        use_secure_urls=False,
    ),
    dict(
        name="eksperimenC1",
        display_name="eksperimen lab C",
        participant_label_file='_rooms/participant_labelsC_sesi1.txt',
        use_secure_urls=False,
    ),
]

# Debugging and admin settings
DEBUG = False
ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')  # Use environment variable for security
AUTH_LEVEL = environ.get('OTREE_AUTH_LEVEL')  # Options: DEMO, STUDY, or full AUTH

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '3860349561509'
