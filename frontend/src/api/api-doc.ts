import axios from 'axios';

export const getSwaggerUrl = () => {
  return `${axios.defaults.baseURL}/docs`;
};

export const getRedocUrl = () => {
  return `${axios.defaults.baseURL}/redoc`;
};
