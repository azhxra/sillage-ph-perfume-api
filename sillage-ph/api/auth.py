"""Sillage PH accounts: Supabase Auth identifies the user; PostgreSQL stores app roles."""
import logging
import os
from uuid import UUID

import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import database as db

logger = logging.getLogger(__name__)
_bearer = HTTPBearer(auto_error=False)


def _auth_config():
    base = os.getenv('SUPABASE_URL', '').strip().rstrip('/')
    key = (os.getenv('SUPABASE_PUBLISHABLE_KEY') or os.getenv('SUPABASE_ANON_KEY') or '').strip()
    if not base.startswith('https://') or not key:
        raise HTTPException(status_code=503, detail='Login service is not configured.')
    return base, key


def _supabase_user(access_token: str):
    base, key = _auth_config()
    try:
        response = requests.get(
            f'{base}/auth/v1/user',
            headers={'apikey': key, 'Authorization': f'Bearer {access_token}'},
            timeout=8,
        )
    except requests.RequestException:
        logger.exception('Supabase Auth validation request failed')
        raise HTTPException(503, 'Authentication temporarily unavailable.') from None
    if response.status_code in (401, 403):
        raise HTTPException(401, 'Invalid or expired session.')
    if response.status_code != 200:
        logger.error('Supabase Auth validation returned HTTP %s', response.status_code)
        raise HTTPException(503, 'Authentication temporarily unavailable.')
    try:
        user = response.json()
        user_id = str(UUID(user['id']))
    except (ValueError, TypeError, KeyError):
        raise HTTPException(503, 'Unexpected authentication response.') from None
    return {'id': user_id, 'email': user.get('email')}


def _app_identity(token: str):
    user = _supabase_user(token)
    role = db.get_app_user_role(user['id'])
    if role is None:
        role = 'user'
    if role not in ('admin', 'user'):
        raise HTTPException(403, 'Account role is not assigned. Contact the site administrator.')
    return {**user, 'role': role}


def login(email: str, password: str):
    base, key = _auth_config()
    try:
        response = requests.post(
            f'{base}/auth/v1/token',
            params={'grant_type': 'password'},
            headers={'apikey': key, 'Content-Type': 'application/json'},
            json={'email': email, 'password': password},
            timeout=8,
        )
    except requests.RequestException:
        logger.exception('Supabase Auth sign-in request failed')
        raise HTTPException(503, 'Authentication temporarily unavailable.') from None
    if response.status_code == 429:
        raise HTTPException(429, 'Too many login attempts. Try again later.')
    if response.status_code in (400, 401, 403, 422):
        raise HTTPException(401, 'Invalid email or password, or email not confirmed.')
    if response.status_code != 200:
        logger.error('Supabase Auth sign-in returned HTTP %s', response.status_code)
        raise HTTPException(503, 'Authentication temporarily unavailable.')
    try:
        payload = response.json()
        token = payload['access_token']
        expires_in = payload.get('expires_in', 3600)
        if not isinstance(token, str) or not token:
            raise ValueError('Empty access token')
    except (ValueError, TypeError, KeyError):
        raise HTTPException(503, 'Unexpected authentication response.') from None
    identity = _app_identity(token)
    return {'access_token': token, 'token_type': 'bearer',
            'expires_in': expires_in, 'id': identity['id'],
            'email': identity['email'], 'role': identity['role']}


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)):
    if credentials is None:
        raise HTTPException(401, 'Sign in to use this endpoint.', headers={'WWW-Authenticate': 'Bearer'})
    return _app_identity(credentials.credentials)


def require_admin(user=Depends(current_user)):
    if user['role'] != 'admin':
        raise HTTPException(403, 'Administrator access required.')
    return user


def signup(email: str, password: str):
    base, key = _auth_config()
    try:
        response = requests.post(
            f'{base}/auth/v1/signup',
            headers={'apikey': key},
            json={'email': email, 'password': password},
            timeout=8,
        )
    except requests.RequestException:
        raise HTTPException(503, 'Sign-up temporarily unavailable.') from None
    if response.status_code == 429:
        raise HTTPException(429, 'Too many attempts. Try again later.')
    if response.status_code in (400, 403, 422):
        raise HTTPException(400, 'Could not create the account. Check your email and password.')
    if not response.ok:
        raise HTTPException(503, 'Sign-up temporarily unavailable.')
    return {'message': 'Account request received. If you receive a confirmation email, confirm your address before signing in.'}
