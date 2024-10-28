import { createRouter, createWebHashHistory } from 'vue-router'
import pinia from "@/stores/index";
import { useUserStore } from '@/stores/user';

const router = createRouter({
  // history: createWebHashHistory(import.meta.env.BASE_URL),
  history: createWebHashHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("../views/Login/LoginView.vue"),
    },
    {
      path: "/",
      component: () => import("../layout/Layout.vue"),
      redirect: "/index",
      children: [
        {
          name: "main",
          path: "main",
          redirect: "/index",
          component: () => import("../views/Chat/Chat.vue"),
          children: [
            {
              name: "index",
              path: "/index",
              component: () =>
                import("../views/Chat/components/Introduction.vue"),
            },
            {
              name: "chat",
              path: "/chat",
              component: () => import("../views/Chat/components/ChatList.vue"),
            },
          ],
        },
        {
          name: "library",
          path: "library",
          component: () => import("../views/Library/Library.vue"),
        },
        {
          name: "fileRecords",
          path: "fileRecords",
          component: () => import("../views/FileRecords/FileRecords.vue"),
        },
      ],
    },
  ],
});

router.beforeEach(async (to, from) => {
  const userStore = useUserStore(pinia);
  if (userStore.user.account === "" && to.name !== "login") {
    return "/login";
  }
});

export default router
