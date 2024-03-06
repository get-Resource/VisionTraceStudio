// import { loadResource } from "./container/fullcalendar/resources.js";
// import { loadResource } from "../../static/utils/resources.js";
const resourceLoadPromises = {};

function loadResource(url) {
  if (resourceLoadPromises[url]) return resourceLoadPromises[url];
  const loadPromise = new Promise((resolve, reject) => {
    const dataAttribute = `data-${url.split("/").pop().replace(/\./g, "-")}`;
    if (document.querySelector(`[${dataAttribute}]`)) {
      resolve();
      return;
    }
    let element;
    if (url.endsWith(".css")) {
      element = document.createElement("link");
      element.setAttribute("rel", "stylesheet");
      element.setAttribute("href", url);
    } else if (url.endsWith(".js")) {
      element = document.createElement("script");
      element.setAttribute("src", url);
    }
    element.setAttribute(dataAttribute, "");
    document.head.appendChild(element);
    element.onload = resolve;
    element.onerror = reject;
  });
  resourceLoadPromises[url] = loadPromise;
  return loadPromise;
}

export default {
  template: "<div></div>",
  props: {
    options: Array,
    resource_path: String,
  },
  async mounted() {
    await this.$nextTick(); // NOTE: wait for window.path_prefix to be set
    await loadResource(window.path_prefix + `${this.resource_path}/index.global.min.js`);
    this.options.eventClick = (info) => this.$emit("click", { info });
    this.calendar = new FullCalendar.Calendar(this.$el, this.options);
    this.calendar.render();
  },
  methods: {
    update_calendar() {
      if (this.calendar) {
        this.calendar.setOption("events", this.options.events);
        this.calendar.render();
      }
    },
  },
};