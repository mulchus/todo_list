from quart import Quart, jsonify, request

def make_quart_app(bot):

    quart_app = Quart(__name__)

    @quart_app.route('/api/notify', methods=['POST'])
    async def notify_about_task():
        data = await request.json
        message = data.get('message', 'No message provided')
        tg_id = data.get('tg_id')
        await bot.send_message(tg_id, message)
        return 'Message sent', 200

    return quart_app
