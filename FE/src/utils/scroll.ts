export const scroll = (element: HTMLElement) => {
  setTimeout(() => {
    element.scrollBy({
      top: element.scrollHeight,
      behavior: "smooth",
    });
  }, 10);
};