import request from '../utils/request'

export function login(data) {
  return request({
    url: '/users/login/',
    method: 'post',
    data
  })
}

export function register(data) {
  return request({
    url: '/users/register/',
    method: 'post',
    data
  })
}

export function getFavorites() {
  return request({
    url: '/users/favorites/',
    method: 'get'
  })
}

export function addFavorite(symbol) {
  return request({
    url: '/users/favorites/',
    method: 'post',
    data: { symbol }
  })
}

export function removeFavorite(symbol) {
  return request({
    url: '/users/favorites/',
    method: 'delete',
    data: { symbol }
  })
}

export function getUserInfo() {
  return request({
    url: '/users/info/',
    method: 'get'
  })
}

export function updateUserInfo(data) {
  return request({
    url: '/users/update/',
    method: 'put',
    data
  })
}

export function deleteAccount() {
  return request({
    url: '/users/account/',
    method: 'delete'
  })
}