ADD_MODERATION_QUERY  = '''
--sql
INSERT INTO public.moderation_results (item_id, status) 
VALUES
    ($1, $2)
RETURNING task_id
; 
'''

GET_AD_QUERY = '''
--sql 
SELECT *
FROM public.ads
INNER JOIN public.sellers
    ON public.sellers.seller_id = public.ads.seller_id
WHERE public.ads.item_id = $1
;
'''

UPDATE_MODERATION_AD_QUERY = '''
--sql
UPDATE public.moderation_results
SET status = $2,
    is_violation = $3,
    probability = $4,
    error_message = $5,
    processed_at = $6
WHERE item_id = $1
RETURNING task_id
;
'''

GET_MODERATION_TASK_FROM_ITEM_ID_QUERY = '''
--sql
SELECT * 
FROM public.moderation_results
WHERE item_id = $1
;
'''

GET_MODERATION_TASK_FROM_TASK_ID_QUERY = '''
--sql
SELECT * 
FROM public.moderation_results
WHERE task_id = $1
;
'''

DELETE_AD_QUERY = '''
--sql
DELETE FROM public.ads
WHERE item_id = $1
'''

ADD_AD_QUERY = """
--sql
INSERT INTO public.ads (
    seller_id,
    item_id,
    name,
    description,
    category,
    images_qty
)
VALUES ($1, $2, $3, $4, $5, $6)
RETURNING ad_id
;
"""

CREATE_ACCOUNT_QUERY = '''
--sql
INSERT INTO public.account (login, password)
VALUES ($1, $2)
RETURNING id
;
'''

GET_ACCOUNT_BY_ID_QUERY = '''
--sql
SELECT *
FROM public.account
WHERE id = $1
;
'''

DELETE_ACCOUNT_QUERY = '''
--sql
DELETE FROM public.account
WHERE id = $1
;
'''

BLOCK_ACCOUNT_QUERY = '''
--sql
UPDATE public.account
SET is_blocked = TRUE
WHERE id = $1
;
'''

GET_ACCOUNT_BY_LOGIN_PASSWORD_QUERY = '''
--sql
SELECT *
FROM public.account
WHERE login = $1 AND password = $2
;
'''
