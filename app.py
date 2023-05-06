from flask import Flask, jsonify, request
from flask.views import MethodView
from models import Session, Advert


app = Flask('app')


class HttpError(Exception):

    def __init__(
            self, status_code: int,
            message: dict | list | str | int | bool
        ):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):
    error_message = {
        'status': 'error',
        'message': error.message
    }
    response = jsonify(error_message)
    response.status_code = error.status_code
    return response


def get_advert(session: Session, advert_id: int):
    advert = session.get(Advert, advert_id)
    if advert is None:
        raise HttpError(404, 'No advert found')
    return advert


class AdvertView(MethodView):

    def get(self, advert_id: int):
        with Session() as session:
            advert = get_advert(session, advert_id)
            return jsonify({
                'id': advert.id,
                'title': advert.title,
                'creation_time': advert.creation_time.isoformat(),
                'owner': advert.owner
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            advert = Advert(**json_data)
            session.add(advert)
            session.commit()
            return jsonify({'id': advert.id})

    def patch(self, advert_id: int):
        json_data = request.json
        with Session() as session:
            advert = get_advert(session, advert_id)
            for field, value in json_data.items():
                setattr(advert, field, value)
            session.add(advert)
            session.commit()
            return jsonify({
                'id': advert.id,
                'title': advert.title,
                'creation_time': advert.creation_time.isoformat(),
                'owner': advert.owner
            })

    def delete(self, advert_id: int):
        with Session() as session:
            advert = get_advert(session, advert_id)
            session.delete(advert)
            session.commit()
            return jsonify({'status': 'Deletion done'})

app.add_url_rule(
    '/advert/<int:advert_id>/',
    view_func=AdvertView.as_view('with_advert_id'),
    methods=['GET', 'PATCH', 'DELETE']
)

app.add_url_rule(
    '/advert/',
    view_func=AdvertView.as_view('create_advert'),
    methods=['POST']
)

if __name__ == '__main__':
    app.run()
