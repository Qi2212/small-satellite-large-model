import { http } from "../utils/http";

/**
 * 注册
 * @param
 */
export const postRegister = (account:string,username:string,password1:string,password2:string): any => {
  return http.post("/api/Users/register", {
    account: account,
    username: username,
    password_1: password1,
    password_2: password2,
  });
};
/**
 * 登录
 * @param
 */
export const postLogin = (account: string,password: string): any => {
  return http.post("/api/Users/login", {
    account: account,
    password: password,
  });
};
