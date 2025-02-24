const regexEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

const validateEmail = (email: string): boolean => {
  return regexEmail.test(email);
};

export default validateEmail;
