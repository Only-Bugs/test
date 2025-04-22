import logging
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pose_detection import run_pose_detection

# --- Logger Setup ---
# Main logger
main_handler = logging.StreamHandler()
main_handler.setLevel(logging.INFO)
main_formatter = logging.Formatter(
    '{asctime} [{levelname}] {name}:{funcName}() - {message}',
    style='{',
    datefmt='%Y-%m-%d %H:%M:%S'
)
main_handler.setFormatter(main_formatter)
logger = logging.getLogger('cloudpose')
logger.setLevel(logging.INFO)
logger.addHandler(main_handler)

# Response logger to file with JSON formatting
response_handler = logging.FileHandler('responses.log')
response_handler.setLevel(logging.INFO)
response_formatter = logging.Formatter(
    '{asctime} - RESPONSE - {message}',
    style='{',
    datefmt='%Y-%m-%d %H:%M:%S'
)
response_handler.setFormatter(response_formatter)
response_logger = logging.getLogger('cloudpose_response')
response_logger.setLevel(logging.INFO)
response_logger.addHandler(response_handler)

# --- FastAPI App ---
app = FastAPI(title='CloudPose', version='1.0')

@app.get('/', summary='Health check')
async def health_check():
    logger.info('Health check endpoint called')
    return {'status': 'alive'}

@app.post('/predict', summary='Detect poses')
async def predict_pose(req: Request):
    # Parse request
    try:
        body_bytes = await req.body()
        data = json.loads(body_bytes)
        if isinstance(data, str):
            logger.info('Double-encoded JSON received, decoding inner string')
            data = json.loads(data)
        if not isinstance(data, dict):
            raise ValueError('Expected JSON object')
    except Exception as e:
        logger.error('JSON parsing failed: %s', e)
        return JSONResponse(status_code=400, content={'error': 'Invalid JSON'})

    req_id = data.get('id', 'N/A')
    image_b64 = data.get('image')
    if not image_b64:
        logger.error('Missing image field (request id=%s)', req_id)
        return JSONResponse(status_code=400, content={'id': req_id, 'error': 'Missing image'})

    # Inference
    try:
        result = run_pose_detection(image_b64)
    except Exception as e:
        logger.exception('Inference error (request id=%s)', req_id)
        return JSONResponse(status_code=500, content={'id': req_id, 'error': 'Inference failed'})

    if result is None:
        logger.error('Inference returned None (request id=%s)', req_id)
        return JSONResponse(status_code=500, content={'id': req_id, 'error': 'No poses detected'})

    # Convert arrays
    if hasattr(result, 'tolist'):
        result = result.tolist()

    response_payload = {'id': req_id, 'keypoints': result}

    # Log response in JSON format
    response_logger.info(json.dumps(response_payload))

    logger.info('Responding to request id=%s with %d keypoints', req_id, sum(len(p) for p in result))
    return response_payload