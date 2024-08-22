import { ref, computed } from "vue";
import { defineStore } from "pinia";

export const useUserStore = defineStore("user", () => {
  const user = ref({
    account: "",
    username: "",
    // token: "",
    type: "",
  });
  // const isLogin = computed(() => {
  //     return user.value.token !== "";
  // });account
  const setUser = (
    account: string,
    username: string,
    type: string,
  ) => {
    user.value = { account,username,type }
  };
  const logout = () => {
    user.value = {
      account: "",
      username: "",
      type: "",
    };
  };
  return {
    user,
    // isLogin,
    setUser,
    logout,
  };
},
{
    persist:true
});