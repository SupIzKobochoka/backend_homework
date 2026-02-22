CHECK_ADS_QUERY = '''
    --sql
    SELECT item_id
    FROM public.ads
    WHERE item_id = $1
    ;
    '''

CHECK_MODERATION_QUERY = '''
    --sql
    SELECT task_id
    FROM public.moderation_results
    WHERE item_id = $1
    ;
    '''

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

GET_MODERATION_AD_QUERY = '''
--sql
SELECT *
FROM public.moderation_results
WHERE task_id = $1
;
'''

UPDATE_MODERATION_AD_QUERY = '''
--sql
UPDATE public.moderation_results
SET status = $2,
    is_violation = $3,
    probability = $4,
    error_message = $5,
    processed_at = $7
WHERE item_id = $1
ON CONFLICT (item_id) DO NOTHING
RETURNING task_id;
;
'''

GET_MODERATION_STATUS_QUERY = '''
--sql 
SELECT status 
FROM public.moderation_results
WHERE item_id = $1 
;
'''