from aiohttp import web
import json
import numpy as np

def send_ok_response(json_data):
  response_body_bytes = bytes(json.dumps(json_data, indent=2), encoding='utf8')

  headers = {
    'Content-Type': 'application/json; charset=utf-8'
  }
  return web.Response(status=200, body=response_body_bytes, headers=headers)

def send_client_error_response(json_data):
  response_body_bytes = bytes(json.dumps(json_data, indent=2), encoding='utf8')

  headers = {
    'Content-Type': 'application/json; charset=utf-8'
  }

  return web.Response(status=400, body=response_body_bytes, headers=headers)


def make_start_handler(storage):
  async def get_start_handler(request):

    game_name = request.query['name'] if 'name' in request.query else ''

    game = storage.create_new_game(game_name)

    return send_ok_response({
      'id': game['id']
    })

  
  return get_start_handler

def make_list_handler(storage):
  async def list_handler(_):

    formatted_games = list(map(lambda game_instance: { 
      'id': game_instance['id'], 
      'name': game_instance['name'],
      'board_is_empty': len(np.where(game_instance['board'] == 0)[0]) == 9
    }, storage.games.values()))

    return send_ok_response(formatted_games)

  return list_handler


def make_status_handler(storage):
  async def get_status_handler(request):
    params = request.query

    if not 'game' in params:
      return send_client_error_response({
        'reason': 'Missing "game" query parameter!'
      })

    try:
      game_id = int(params['game'])
    except Exception:
      return send_client_error_response({
        'reason': 'Invalid "game" query parameter! Expected positive integer.'
      })


    if not storage.game_exists(game_id):
      return send_client_error_response({
        'error': 'Game with id %d does not exist.' % game_id
      })

    status = storage.get_game_status(game_id)

    return send_ok_response(status)
  
  return get_status_handler

def make_play_handler(storage):
  async def get_play_handler(request):
    params = request.query

    if not 'game' in params:
      return send_client_error_response({
        'reason': 'Missing "game" query parameter!'
      })

    if not 'x' in params:
      return send_client_error_response({
        'reason': 'Missing "x" query parameter!'
      })

    if not 'y' in params:
      return send_client_error_response({
        'reason': 'Missing "y" query parameter!'
      })

    if not 'player' in params:
      return send_client_error_response({
        'reason': 'Missing "player" query parameter!'
      })

    try:
      game_id = int(params['game'])
      x = int(params['x'])
      y = int(params['y'])
      player_id = int(params['player'])
    except ValueError:
      return send_client_error_response({
        'reason': 'Parameters "game", "x", "y", "player" must be integers!'
      })


    if not storage.game_exists(game_id):
      return send_client_error_response({
        'error': 'Game with id %d does not exist.' % game_id
      })

    if player_id != 1 and player_id != 2:
      return send_client_error_response({
        'error': 'Invalid player id.'
      })


    return send_ok_response(storage.make_move(game_id, x, y, player_id))



  return get_play_handler
