const list = document.getElementById("church-list");
const template = document.getElementById("church-item-template");
const params = new URLSearchParams(window.location.search);
const region = (params.get("region") || "all").toLowerCase();

async function loadChurches() {
  const response = await fetch("churches.json");
  if (!response.ok) {
    throw new Error("Could not load churches data.");
  }
  return response.json();
}

function formatRegionLabel(regionName) {
  if (!regionName || regionName === "all") return "All Churches";
  return regionName.charAt(0).toUpperCase() + regionName.slice(1);
}

function filterByRegion(churches, regionName) {
  if (!regionName || regionName === "all") return churches;
  return churches.filter((church) => {
    if (!church.region) return true;
    return church.region.toLowerCase() === regionName;
  });
}

function sortChurches(churches) {
  return [...churches].sort((a, b) =>
    (a.name || "").localeCompare(b.name || "", undefined, {
      sensitivity: "base",
    })
  );
}

function updateHeading(regionName) {
  const heading = document.querySelector("h1");
  if (!heading) return;
  const suffix = regionName && regionName !== "all" ? ` — ${formatRegionLabel(regionName)}` : "";
  const title = `Church Directory${suffix}`;
  heading.textContent = title;
  document.title = title;
}

function renderChurches(churches) {
  const fragment = document.createDocumentFragment();

  churches.forEach((church) => {
    const item = template.content.firstElementChild.cloneNode(true);
    const link = item.querySelector(".church-link");
    const name = item.querySelector(".church-name");
    const number = item.querySelector(".church-number");
    const peopleLink = item.querySelector(".church-link-people");
    const facebookLink = item.querySelector(".church-link-facebook");
    const websiteLink = item.querySelector(".church-link-website");

    link.href = church.url;
    name.textContent = church.name;
    number.textContent = `Charity number: ${church.charityNumber}`;

    if (church.urlPeople) {
      peopleLink.href = church.urlPeople;
    } else {
      peopleLink.remove();
    }

    if (church.faceBook) {
      facebookLink.href = church.faceBook;
    } else {
      facebookLink.remove();
    }

    if (church.website) {
      websiteLink.href = church.website;
    } else {
      websiteLink.remove();
    }

    fragment.appendChild(item);
  });

  list.replaceChildren(fragment);
}

function renderError(message) {
  list.innerHTML = "";
  const errorItem = document.createElement("li");
  errorItem.className = "church-card";
  errorItem.textContent = message;
  errorItem.style.padding = "12px";
  list.appendChild(errorItem);
}

loadChurches()
  .then((churches) => {
    const filtered = filterByRegion(churches, region);
    const sorted = sortChurches(filtered);
    updateHeading(region);
    if (sorted.length === 0) {
      renderError(`No churches found for ${formatRegionLabel(region)}.`);
      return;
    }
    renderChurches(sorted);
  })
  .catch((error) => {
    renderError(error.message);
  });
