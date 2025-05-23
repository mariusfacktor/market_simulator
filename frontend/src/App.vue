
// npm run dev


// Push frontend changes
// cd frontend
// npm run build
// cd ..
// git add frontend
// git commit -m "rebuilt frontend"
// git push origin main
// git subtree push --prefix frontend/dist origin gh-pages


<script>

import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Message from 'primevue/message';
import Select from 'primevue/select';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import SelectButton from 'primevue/selectbutton';
import InputNumber from 'primevue/inputnumber';
import ToggleSwitch from 'primevue/toggleswitch';
import Tag from 'primevue/tag';
import Chart from 'primevue/chart';

// https://www.npmjs.com/package/vue-toast-notification
import {useToast} from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

import axios from 'axios';


const $toast = useToast();


export default {


  components: {
    InputText,
    Button,
    Message,
    Select,
    DataTable,
    Column,
    SelectButton,
    InputNumber,
    ToggleSwitch,
    Tag,
    Chart,
  },

  data() {
    return {

      // addr: 'http://127.0.0.1' + ':' + '8000',
      // addr: 'http://34.82.55.106' + ':' + '8000',
      // addr: 'https://market-sim.duckdns.org',
      addr: 'https://market-sim.serverpit.com',

      data_getSellOrders: null,
      data_getBuyOrders: null,

      data_getPriceSell: null,
      data_getPriceBuy: null,


      data_getAssets: null,
      data_getPeople: null,
      data_getResources: null,

      data_createPerson: null,

      data_sell: null,
      data_buy: null,

      data_cancelSellOrder: null,
      data_cancelBuyOrder: null,

      error: null,

      selectedPerson: '',
      createdPerson: '',
      currentPerson: '',

      money: null,
      selectedResource: null,
      sellQuantity: null,
      sellPrice: null,

      currentPersonSellOrders: null,
      selectedSellOrderForCancel: null,

      currentPersonBuyOrders: null,
      selectedBuyOrderForCancel: null,

      currentResource: null,
      selectedSale: null,
      data_getSellOrdersForBuying: null,
      data_getBuyOrdersForSelling: null,

      buyQuantity: null,
      buyPrice: null,

      numAvailableToBuy: null,
      numAvailableToSell: null,

      pricePerUnitSell: null,
      pricePerUnitBuy: null,

      firstPriceSell: null,
      firstPriceBuy: null,


      adminToggle: null,
      adminMoney: null,
      adminDepositWithdraw: null,

      adminDepositWithdrawResponse: null,

      adminSelectMoneyOrResorce: null,
      adminSelectedResource: null,
      adminResourceAmount: null,
      adminDepositWithdrawResource: null,
      adminGiveOrTakeResourceResponse: null,

      newResourceData: null,
      selectButtonResource: null,

      newResourceType: null,

      typingSessionKey: null,
      sessionKey: null,

      data_sessionKey: null,

      filters: {global: { value: null, matchMode: 'contains' }},

      data_supply_demand: { labels: [],
                           datasets: [
                            { label: 'supply',
                              data: [],
                              fill: false,
                              borderColor: '#238bad',
                              tension: 0.0,
                            },

                            { label: 'demand',
                              data: [],
                              fill: false,
                              borderColor: '#e65d45',
                              tension: 0.0,

                            },
                           ]
                          },


      chartOptions: {
        responsive: true,

        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: false,
            text: 'supply and demand'
          }
        },

        scales: {
          x: {
            title: {
              display: true,
              text: 'quantity'
            }
          },
          y: {
            title: {
              display: true,
              text: 'price'
            }
          }
        },

        animation: {
          duration: 0 // No animation = no jumping
        },

      },


    };
  },

  mounted() {
    document.title = 'Market Simulator'; // set site title
    setInterval(this.updateEverything, 1000); // refresh all data from backend (works with gunicorn but not flask directly)
  },

  methods: {

    makeToast(message, b_success=true) {

      var success_str;

      if (b_success) {
        success_str = 'success';
      }
      else {
        success_str = 'error';
      }

      this.$toast.open({
        message: message,
        type: success_str, // success, info, warning, error, default
        position: 'bottom-right',
        duration: 3000,
      });
    },


    calculate_supply_and_demand_graph() {

      let max_quantity = Math.max(this.numAvailableToBuy, this.numAvailableToSell);


      // Supply
      let supply_running_quantity = 0;

      let supply_price_list = [];
      let supply_quantity_list = [];

      for (let i = 0; i < this.data_getSellOrdersForBuying.data.orders_list.length; i++) {
        let supply_curr_price = this.data_getSellOrdersForBuying.data.orders_list[i].price;
        supply_running_quantity += this.data_getSellOrdersForBuying.data.orders_list[i].quantity_available;

        supply_price_list.push(supply_curr_price);
        supply_quantity_list.push(supply_running_quantity);
      }



      // Demand
      let demand_running_quantity = 0;

      let demand_price_list = [];
      let demand_quantity_list = [];

      for (let i = 0; i < this.data_getBuyOrdersForSelling.data.orders_list.length; i++) {
        let demand_curr_price = this.data_getBuyOrdersForSelling.data.orders_list[i].price;
        demand_running_quantity += this.data_getBuyOrdersForSelling.data.orders_list[i].quantity_available;

        demand_price_list.push(demand_curr_price);
        demand_quantity_list.push(demand_running_quantity);

      }


      let graph_quantity_list = [];
      let graph_supply_price_list = [];
      let graph_demand_price_list = [];

      let prev_supply_price = 0;
      let prev_demand_price = this.firstPriceBuy;

      for (let i = 0; i < max_quantity + 1; i++) {
        graph_quantity_list.push(i);

        let supply_idx = supply_quantity_list.indexOf(i);
        let demand_idx = demand_quantity_list.indexOf(i);

        if (supply_idx !== -1) {
          graph_supply_price_list.push(supply_price_list[supply_idx]);
          prev_supply_price = supply_price_list[supply_idx];
        }
        else {
          graph_supply_price_list.push(prev_supply_price)
        }

        if (demand_idx !== -1) {
          graph_demand_price_list.push(demand_price_list[demand_idx]);

          if (demand_idx == demand_quantity_list.length - 1) {
            // end of list
            prev_demand_price = 0;
          }
          else {
            prev_demand_price = demand_price_list[demand_idx];
          }
        }
        else {
          graph_demand_price_list.push(prev_demand_price);
        }

      }

      this.data_supply_demand['labels'] = graph_quantity_list;
      this.data_supply_demand['datasets'][0]['data'] = graph_supply_price_list;
      this.data_supply_demand['datasets'][1]['data'] = graph_demand_price_list;

    },


    async updateEverything() {

      if (this.sessionKey) {

        // Get list of resources
        await this.getResources();

        // Get list of people
        await this.getPeople();


        if (this.currentPerson) {

          // Get money and resources for current person
          await this.getAssets(this.currentPerson);


          if (this.currentResource !== null) {
            // Get updated sell orders
            await this.getSellOrdersForPerson(this.currentResource);

            // Get updated buy orders
            await this.getBuyOrdersForPerson(this.currentResource);
          }

        }

        if (this.currentResource !== null) {

          // Get sell orders and price to buy
          await this.getSellOrdersForBuying(this.currentResource);

          // Get buy orders and price to sell
          await this.getBuyOrdersForSelling(this.currentResource);

          this.calculate_supply_and_demand_graph();
        }



      }

    },


    async getOrders(resource_type, name=null, b_quantity_available=false, b_buy_orders=false) {
      try {

        let url = this.addr + '/get_orders'

        const headers = { 'Content-Type': 'application/json' };
        var params = {  'session_key': this.sessionKey,
                        'resource_type': resource_type
                      };

        if (name !== null) {
          params['name'] = name;
        }

        if (b_quantity_available) {
          params['b_quantity_available'] = true;
        }

        if (b_buy_orders) {
          params['b_buy_orders'] = true;
        }

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers,
          params: params,
        });

        console.log(response.data);

        if (b_buy_orders) {
          this.data_getBuyOrders = response.data;
        }
        else {
          this.data_getSellOrders = response.data;
        }

        this.error = null;
      } catch (err) {
        this.data_getSellOrders = null;
        this.data_getBuyOrders = null;
        this.error = err.message;
      }

    },

    async getPrice(resource_type, quantity, b_sell_price=true) {
      try {

        let url = this.addr + '/get_price'

        const headers = { 'Content-Type': 'application/json' };


        var params = { 'session_key': this.sessionKey,
                         'resource_type': resource_type,
                         'quantity': quantity };

        if (b_sell_price) {
          params['b_sell_price'] = true;
        }
        else {
          params['b_sell_price'] = false;
        }

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers,
          params: params,
        });

        console.log(response.data);

        if (b_sell_price) {
          this.data_getPriceSell = response.data;

          this.pricePerUnitSell = this.data_getPriceSell.data.price / quantity;
          this.pricePerUnitSell = this.pricePerUnitSell.toFixed(2);
        }
        else {
          this.data_getPriceBuy = response.data;

          this.pricePerUnitBuy = this.data_getPriceBuy.data.price / quantity;
          this.pricePerUnitBuy = this.pricePerUnitBuy.toFixed(2);
        }


        this.error = null;

      } catch (err) {

        this.data_getPriceSell = null;
        this.pricePerUnitSell = null;

        this.data_getPriceBuy = null;
        this.pricePerUnitBuy = null;

        this.error = err.message;
      }
    },

    async getAssets(name) {
      try {

        let url = this.addr + '/get_assets'

        const headers = { 'Content-Type': 'application/json' };
        const params = {  'session_key': this.sessionKey,
                          'name': String(name) 
                        };

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getAssets = response.data;
        this.error = null;

        this.money = this.data_getAssets.data.cash;

      } catch (err) {
        this.data_getAssets = null;
        this.error = err.message;
      }

    },

    async getPeople() {
      try {

        let url = this.addr + '/get_people'

        const headers = { 'Content-Type': 'application/json' };
        const params = {  'session_key': this.sessionKey,
                        };

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getPeople = response.data;
        this.error = null;
      } catch (err) {
        this.data_getPeople = null;
        this.error = err.message;
      }
    },


    async getResources() {
      try {

        let url = this.addr + '/get_resources'

        const headers = { 'Content-Type': 'application/json' };
        const params = {  'session_key': this.sessionKey,
                        };

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getResources = response.data;
        this.error = null;
      } catch (err) {
        this.data_getResources = null;
        this.error = err.message;
      }
    },


    async createPerson(name) {

      if (name == '') {

        this.makeToast('Missing info', false);

        return;
      }

      let response;

      try {

        let url = this.addr + '/create_person'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': String(name),
                       'cash': 0,
                       'resource_dict': {} };
                       // 'resource_dict': {'apple': 4} };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_createPerson = response.data;
        this.error = null;
      } catch (err) {
        this.data_createPerson = null;
        this.error = err.message;
      }

      // set currentPerson
      this.setCurrentPerson(name);

      // Update
      this.getPeople();

      this.makeToast(response.data.message, response.data.b_success);

    },


    async buy_order(name, resource_type, quantity, price) {

      if (name === null || resource_type === null || quantity === null || price === null) {

        this.makeToast('Missing info', false);

        return;
      };

      let response;

      try {

        let url = this.addr + '/buy_order'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': name,
                       'resource_type': resource_type,
                       'quantity': quantity,
                       'price': price };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        // reset fields
        this.buyQuantity = null;
        this.buyPrice = null;

        this.data_buy = response.data;
        this.error = null;


        // update everything
        await this.updateEverything();

      } catch (err) {
        this.data_buy = null;
        this.error = err.message;
      }

      this.makeToast(response.data.message, response.data.b_success);

    },



    async sell_order(name, resource_type, quantity, price) {

      if (name === null || resource_type === null || quantity === null || price === null) {

        this.makeToast('Missing info', false);

        return;
      };

      let response;

      try {

        let url = this.addr + '/sell_order'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': name,
                       'resource_type': resource_type,
                       'quantity': quantity,
                       'price': price };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);


        // reset fields
        this.sellQuantity = null;
        this.sellPrice = null;

        this.data_sell = response.data;
        this.error = null;


        // update everything
        await this.updateEverything();

      } catch (err) {
        this.data_sell = null;
        this.error = err.message;
      }

      this.makeToast(response.data.message, response.data.b_success);

    },

    async buy_now(name, resource_type, quantity) {

      let response;

      try {

        let url = this.addr + '/buy_now'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': name,
                       'resource_type': resource_type,
                       'quantity': quantity };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_buy = response.data;
        this.error = null;
      } catch (err) {
        this.data_buy = null;
        this.error = err.message;
      }


      // reset
      this.buyQuantity = null;

      // update everything
      await this.updateEverything();

      this.makeToast(response.data.message, response.data.b_success);

    },


    async sell_now(name, resource_type, quantity) {

      let response;

      try {

        let url = this.addr + '/sell_now'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': name,
                       'resource_type': resource_type,
                       'quantity': quantity };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_sell = response.data;
        this.error = null;
      } catch (err) {
        this.data_sell = null;
        this.error = err.message;
      }

      // reset
      this.sellQuantity = null;

      // update everything
      await this.updateEverything();

      this.makeToast(response.data.message, response.data.b_success);

    },


    async sell_now_or_sell_order() {

      if (this.currentPerson === null || this.currentResource === null || this.sellQuantity === null) {

        this.makeToast('Missing info', false);

        return;
      }

      if (this.sellPrice != null) {
        await this.sell_order(this.currentPerson, this.currentResource, this.sellQuantity, this.sellPrice);
      }
      else {
        await this.sell_now(this.currentPerson, this.currentResource, this.sellQuantity);
      }

    },


    async buy_now_or_buy_order() {

      if (this.currentPerson === null || this.currentResource === null || this.buyQuantity === null) {

        this.makeToast('Missing info', false);

        return;
      }

      if (this.buyPrice != null) {
        await this.buy_order(this.currentPerson, this.currentResource, this.buyQuantity, this.buyPrice);
      }
      else {
        await this.buy_now(this.currentPerson, this.currentResource, this.buyQuantity);
      }

    },


    async cancelSellOrder(sell_id) {
      try {

        let url = this.addr + '/cancel_sell_order'

        const headers = { 'Content-Type': 'application/json' };

        const body = {  'session_key': this.sessionKey,
                        'sell_id': sell_id 
                      };

        const response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_cancelSellOrder = response.data;
        this.error = null;
      } catch (err) {
        this.data_cancelSellOrder = null;
        this.error = err.message;
      }

      // update everything
      await this.updateEverything();

      // reset
      this.selectedSellOrderForCancel = null;

    },



    async cancelBuyOrder(buy_id) {
      try {

        let url = this.addr + '/cancel_buy_order'

        const headers = { 'Content-Type': 'application/json' };

        const body = {  'session_key': this.sessionKey,
                        'buy_id': buy_id 
                      };

        const response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_cancelBuyOrder = response.data;
        this.error = null;
      } catch (err) {
        this.data_cancelBuyOrder = null;
        this.error = err.message;
      }

      // update everything
      await this.updateEverything();

      // reset
      this.selectedBuyOrderForCancel = null;

    },



    async getSellOrdersForPerson(resource_type) {

      await this.getOrders(resource_type, this.currentPerson);

      if (this.currentPerson) {
        this.currentPersonSellOrders = this.data_getSellOrders.data.orders_list;
      }
      else {
        this.currentPersonSellOrders = null;
      }

    },


    async getBuyOrdersForPerson(resource_type) {

      await this.getOrders(resource_type, this.currentPerson, false, true);

      if (this.currentPerson) {
        this.currentPersonBuyOrders = this.data_getBuyOrders.data.orders_list;
      }
      else {
        this.currentPersonBuyOrders = null;
      }

    },


    async setCurrentPerson(name) {
      this.currentPerson = name;
      this.selectedPerson = name;

      await this.getAssets(name);

      if (this.currentResource !== null) {
        // get updated sell orders
        await this.getSellOrdersForPerson(this.currentResource)

        // get updated buy orders
        await this.getBuyOrdersForPerson(this.currentResource)
      }

      // reset
      this.selectedResource = null;
      this.selectedSellOrderForCancel = null;
      this.selectedBuyOrderForCancel = null;

    },

    async setCurrentResource(resource_type) {
      this.currentResource = resource_type;

      if (this.currentPerson !== null) {
        // get updated sell orders
        await this.getSellOrdersForPerson(resource_type);

        // get updated buy orders
        await this.getBuyOrdersForPerson(this.currentResource)
      }

      await this.getSellOrdersForBuying(resource_type);
      await this.getBuyOrdersForSelling(resource_type);

      // reset
      if (this.selectedResource !== null) {
        if (this.selectedResource.type != resource_type) {
          this.selectedResource = null;
        }
      }

      // reset
      this.selectedSellOrderForCancel = null;
      this.selectedBuyOrderForCancel = null;

      this.calculate_supply_and_demand_graph();

    },



    async getSellOrdersForBuying(resource_type) {

      await this.getOrders(resource_type, null, true);

      this.data_getSellOrdersForBuying = this.data_getSellOrders;

      // Add up all the quantities to get total number for sale
      var numAvailable = 0;
      for (let i = 0; i < this.data_getSellOrdersForBuying.data.orders_list.length; i++) {
        numAvailable += this.data_getSellOrdersForBuying.data.orders_list[i].quantity_available;
      }

      // Get first price
      if (this.data_getSellOrdersForBuying.data.orders_list.length > 0) {
        this.firstPriceSell = this.data_getSellOrdersForBuying.data.orders_list[0].price;
      }
      else {
        this.firstPriceSell = null;
      }

      this.numAvailableToBuy = numAvailable;


    },



    async getBuyOrdersForSelling(resource_type) {

      await this.getOrders(resource_type, null, true, true);

      this.data_getBuyOrdersForSelling = this.data_getBuyOrders;

      // Add up all the quantities to get total number for sale
      var num_available = 0;
      for (let i = 0; i < this.data_getBuyOrdersForSelling.data.orders_list.length; i++) {
        num_available += this.data_getBuyOrdersForSelling.data.orders_list[i].quantity_available;
      }

      // Get first price
      if (this.data_getBuyOrdersForSelling.data.orders_list.length > 0) {
        this.firstPriceBuy = this.data_getBuyOrdersForSelling.data.orders_list[0].price;
      }
      else {
        this.firstPriceBuy = null;
      }

      this.numAvailableToSell = num_available;


    },


    async depositOrWithdraw() {

      if (this.currentPerson === null || this.adminMoney === null || this.adminDepositWithdraw === null) {

        // toast
        this.makeToast('Missing info', false);

        return;
      }

      let response;

      try {

        var b_deposit = false;
        if (this.adminDepositWithdraw == 'Deposit') {
          // add money
          b_deposit = true;
        }
        else {
          // subract money
          b_deposit = false;
        }

        let url = this.addr + '/deposit_or_withdraw'

        const headers = { 'Content-Type': 'application/json' };
        const body = { 'session_key': this.sessionKey,
                       'name': this.currentPerson,
                       'b_deposit': b_deposit,
                       'dollars': this.adminMoney
                      };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.adminDepositWithdrawResponse = response.data;
        this.error = null;
      } catch (err) {
        this.adminDepositWithdrawResponse = null;
        this.error = err.message;
      }

      // update everything
      await this.updateEverything();

      this.makeToast(response.data.message, response.data.b_success);

    },


    async giveOrTakeResource() {

      if (this.currentResource === null || this.currentPerson === null || this.adminResourceAmount === null || this.adminDepositWithdrawResource === null)  {

        this.makeToast('Missing info', false);

        return;
      }

      let response;

      try {

        var b_deposit = false;
        if (this.adminDepositWithdrawResource == 'Deposit') {
          // add money
          b_deposit = true;
        }
        else {
          // subract money
          b_deposit = false;
        }

        let url = this.addr + '/give_or_take_resource'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': this.currentPerson,
                       'resource_type': this.currentResource,
                       'b_deposit': b_deposit,
                       'quantity': this.adminResourceAmount
                      };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.adminGiveOrTakeResourceResponse = response.data;
        this.error = null;
      } catch (err) {
        this.adminGiveOrTakeResourceResponse = null;
        this.error = err.message;
      }

      // update everything
      await this.updateEverything();

      this.makeToast(response.data.message, response.data.b_success);

    },


    async newResource(resource_type) {

      if (resource_type === null) {

        this.makeToast('Missing info', false);

        return;
      }

      let response;

      try {

        let url = this.addr + '/new_resource'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 
                       'session_key': this.sessionKey,
                       'resource_type': String(resource_type)
                      };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.newResourceData = response.data;
        this.error = null;
      } catch (err) {
        this.newResourceData = null;
        this.error = err.message;
      }

      // reset
      this.newResourceType = null;

      // reset
      this.selectedSellOrderForCancel = null;
      this.selectedBuyOrderForCancel = null;

      // update
      await this.getResources();

      this.currentResource = resource_type;

      this.makeToast(response.data.message, response.data.b_success);

    },



    async setSessionKey() {
      this.sessionKey = this.typingSessionKey;
      this.typingSessionKey = null;

      if (this.sessionKey === null) {
        // reset
        this.data_getPeople = null;
        this.currentPerson = null;
        this.money = null;
        this.data_getAssets = null;
        this.currentResource = null;
        this.data_getResources = null;
        this.selectedResource = null;
        this.adminToggle = null;
        this.selectedPerson = '';
        this.selectedSellOrderForCancel = null;
        this.selectedBuyOrderForCancel = null;

        this.makeToast('Missing info', false);

        return;
      }

      let response;

      try {

        let url = this.addr + '/create_session';

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_sessionKey = response.data;
        this.error = null;
      } catch (err) {
        this.data_sessionKey = null;
        this.error = err.message;
      }

      // reset
      this.currentPerson = null;
      this.money = null;
      this.data_getAssets = null;
      this.currentResource = null;
      this.data_getResources = null;
      this.selectedResource = null;
      this.adminToggle = null;

      // Get list of resources
      await this.getResources();

      // Get list of people
      await this.getPeople();

      this.makeToast(response.data.message, response.data.b_success);

    },


    chooseSeverityStatus(quantity, quantity_available) {

      // success, warn, danger, info, primary, secondary, contrast

      var return_str = ""

      if (quantity_available == 0) {
        return_str = "danger";
      }
      else if (quantity == quantity_available) {
        return_str = "success";
      }
      else {
        return_str = "warn";
      }

      return return_str;

    },



    async debugFunc() {
      console.log('DEBUG A0')
    },

 


  },

};



</script>





<template>


  <div :style="{ backgroundColor: '#f0f2f5' }">



    <div class="flexbox-container-top">
      <div class="flexbox-item flexbox-item-4">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-2xl text-center">
            <i class="pi pi-key" style="font-size: 2.0rem;"></i>
            Session
          </p>
        </div>

        <div v-if="sessionKey">
          <p style="font-weight: bold;" class="relative text-lg text-center text-blue-500">{{ sessionKey }}</p>
        </div>
        <div v-else>
          <p class="relative text-lg text-center">enter a session key</p>
        </div>

        <div style="text-align:center;">
          <InputText type="text" v-model="typingSessionKey" placeholder="session key" size="small" style="text-align:center;" @keyup.enter="setSessionKey" />
        
          <Button size="small" type="submit" severity="info" label="Submit" @click="setSessionKey" />
        </div>

      </div>



      <div class="flexbox-item flexbox-item-6">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-2xl text-center">
            <i class="pi pi-user" style="font-size: 2.0rem"></i>
            Person
          </p>
        </div>

        <div v-if="currentPerson">
          <p style="font-weight: bold;" class="relative text-lg text-center text-blue-500">{{ currentPerson }}</p>
        </div>
        <div v-else>
          <p class="relative text-lg text-center">select a person</p>
        </div>


        <div v-if="data_getPeople" style="text-align:center;">
          <Select v-model="selectedPerson" :options="data_getPeople.data.people" placeholder="person" size="small" class="w-full md:w-56"  filter @update:modelValue="setCurrentPerson(selectedPerson)"/>
        </div>

      </div>



      <div class="flexbox-item flexbox-item-7">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-2xl text-center">
            <i class="pi pi-ticket" style="font-size: 2.0rem"></i>
            Resource
          </p>
        </div>


        <div v-if="currentResource">
          <p style="font-weight: bold;" class="relative text-lg text-center text-blue-500">{{ currentResource }}</p>
        </div>
        <div v-else>
          <p class="relative text-lg text-center">select a resource</p>
        </div>


        <div v-if="data_getResources && sessionKey" style="text-align:center;">
          <Select v-model="currentResource" :options="data_getResources.data.resources" placeholder="resource" size="small" class="w-full md:w-56" filter @update:modelValue="setCurrentResource(currentResource)"/>
        </div>


      </div>



    </div>







    <div class="flexbox-container">

      <div class="flexbox-item-colorless flexbox-item-1">





        <div class="flexbox-item-sub flexbox-item-8">

          <div style="text-align:center;">
            <p style="display:inline-block;" class="relative text-2xl text-center">
              <i class="pi pi-money-bill" style="font-size: 2.0rem"></i>
              Assets
            </p>
          </div>
          <br>




          <div v-if="data_getAssets">


            <DataTable v-model:filters="filters" selectionMode="single" v-model:selection="selectedResource" :value="data_getAssets.data.resource_list" size="small" scrollable scrollHeight="204px" tableStyle="min-width: 10rem" @row-select="setCurrentResource(selectedResource.type)" >

              <template #header>
                <span style="font-weight: bold;" class="p-2 relative text-lg" >Money: &nbsp; ${{money.toFixed(2)}}</span>
                
                <InputText v-model="filters['global'].value" placeholder="keyword search" size="small" />

              </template>

              <Column field="type" header="Resource"></Column>
              <Column field="quantity" header="Quantity"></Column>
            </DataTable>

          </div>

          <br>



          <div v-if="currentPerson">

            <div style="text-align:center;">
              <SelectButton v-model="adminDepositWithdraw" :options="['Deposit', 'Withdraw']" size="small" />

              <InputNumber v-model="adminMoney" placeholder="dollar amount" inputId="currency-us" mode="currency" currency="USD" locale="en-US" size="small" />

              <Button size="small" type="submit" severity="info" label="Submit" @click="depositOrWithdraw" />
            </div>

          </div>



            <br>


          <div v-if="currentPerson && currentResource">


            <div style="text-align:center;">
              <SelectButton v-model="adminDepositWithdrawResource" :options="['Deposit', 'Withdraw']" size="small" />

              <InputNumber v-model="adminResourceAmount" placeholder="resource quantity" inputId="integeronly" size="small" />

              <Button size="small" type="submit" severity="info" label="Submit" @click="giveOrTakeResource" />
            </div>

          </div>



        </div>






        <div class="flexbox-item-sub flexbox-item-9">

          <div style="text-align:center;">
            <p style="display:inline-block;" class="relative text-2xl text-center">
              <i class="pi pi-building-columns" style="font-size: 2.0rem"></i>
              Admin
            </p>
          </div>
          <br>


          <div v-if="sessionKey" >

            <div style="text-align:center;">
              <InputText type="text" v-model="createdPerson" placeholder="new person name" size="small" style="text-align:center;" />

                <Button size="small" type="submit" severity="info" label="Submit" @click="createPerson(createdPerson)" />
            </div>
          </div>

          <br>





          <div v-if="sessionKey" >

            <div style="text-align:center;">
              <InputText type="text" v-model="newResourceType" placeholder="new resource" size="small" style="text-align:center;" />

              <Button size="small" type="submit" severity="info" label="Submit" @click="newResource(newResourceType)" />
            </div>
          </div>

        </div>


      </div>






      <div class="flexbox-item-colorless flexbox-item-2">

        <div class="flexbox-item-sub flexbox-item-10">

          <div style="text-align:center;">
            <p style="display:inline-block;" class="relative text-2xl text-center">
              <i class="pi pi-shop" style="font-size: 2.0rem"></i>
              Sell
            </p>
          </div>


          <div v-if="currentResource && data_getBuyOrdersForSelling">
            <div v-if="firstPriceBuy">
                <p class="relative text-lg text-center">Available: {{numAvailableToSell}} &nbsp; &nbsp; &nbsp; Price: ${{firstPriceBuy.toFixed(2)}}</p>
            </div>
            <div v-else>
              <p class="relative text-lg text-center">Available: {{numAvailableToSell}}</p>
            </div>
          </div>



          <div v-if="currentPerson && currentResource">


            <div style="text-align:center;">

              <InputNumber v-model="sellQuantity" inputId="integeronly" placeholder="quantity" :model-value="sellQuantity" size="small" style="text-align:center;" @update:modelValue="getPrice(currentResource, sellQuantity, false)" />

              <InputNumber v-model="sellPrice" inputId="price_input" mode="currency" currency="USD" placeholder="price (optional)" :model-value="sellPrice" size="small" style="text-align:center;" />


                <Button size="small" type="submit" severity="info" label="Submit" @click="sell_now_or_sell_order()" />
            </div>


            <div v-if="sellQuantity && data_getPriceBuy && data_getPriceBuy.data.price">
              <p class="relative text-lg text-center">Total Price: &nbsp; ${{data_getPriceBuy.data.price.toFixed(2)}} &nbsp; &nbsp; &nbsp; Unit Price &nbsp; ${{pricePerUnitBuy}}</p>
            </div>
            <div v-else>
              <p class="relative text-lg text-center"><br></p>
            </div>




            <p class="relative text-lg text-center">your sell orders</p>

            <DataTable selectionMode="single" v-model:selection="selectedSellOrderForCancel" :value="currentPersonSellOrders" size="small" scrollable scrollHeight="190px" tableStyle="min-width: 10rem" >
              <Column field="price" header="Price">
                <template #body="slotProps">
                  <span>${{ slotProps.data.price.toFixed(2) }}</span>
                </template>
              </Column>
              <Column field="quantity" header="Quantity"></Column>
              <Column field="quantity_available" header="Quantity Available">
                <template #body="slotProps">
                  <Tag :value="slotProps.data.quantity_available" :severity="chooseSeverityStatus(slotProps.data.quantity, slotProps.data.quantity_available)" />
                </template>
              </Column>
            </DataTable>

            <div v-if="selectedSellOrderForCancel" >
              <Button style="width: 100%;" type="submit" severity="info" label="cancel listing" size="small" @click="cancelSellOrder(selectedSellOrderForCancel.id)" rounded />
            </div>


          </div>

        </div>



        <div class="flexbox-item-sub flexbox-item-11">


          <div style="text-align:center;">
            <p style="display:inline-block;" class="relative text-2xl text-center">
              <i class="pi pi-chart-line" style="font-size: 2.0rem"></i>
              Market
            </p>
          </div>


          <div v-if="currentResource && data_getSellOrdersForBuying && data_getBuyOrdersForSelling">
            <Chart type="line" :data="data_supply_demand" :options="chartOptions" />
          </div>

        </div>



      </div>









      <div class="flexbox-item-colorless flexbox-item-3">

        <div class="flexbox-item-sub flexbox-item-12">

          <div style="text-align:center;">
            <p style="display:inline-block;" class="relative text-2xl text-center">
              <i class="pi pi-shopping-bag" style="font-size: 2.0rem"></i>
              Buy
            </p>
          </div>


          <div v-if="currentResource && data_getSellOrdersForBuying">

            <div v-if="firstPriceSell">
              <p class="relative text-lg text-center">Available: {{numAvailableToBuy}} &nbsp; &nbsp; &nbsp; Price: ${{firstPriceSell.toFixed(2)}}</p>
            </div>
            <div v-else>
              <p class="relative text-lg text-center">Available: {{numAvailableToBuy}}</p>
            </div>


            <div v-if="currentPerson">


              <div style="text-align:center;">

                <InputNumber v-model="buyQuantity" inputId="integeronly" placeholder="quantity" :model-value="buyQuantity" size="small" style="text-align:center;" @update:modelValue="getPrice(currentResource, buyQuantity)" />

                <InputNumber v-model="buyPrice" inputId="price_input" mode="currency" currency="USD" placeholder="price (optional)" :model-value="buyPrice" size="small" style="text-align:center;" />


                  <Button size="small" type="submit" severity="info" label="Submit" @click="buy_now_or_buy_order()" />
              </div>



              <div v-if="buyQuantity && data_getPriceSell && data_getPriceSell.data.price">
                <p class="relative text-lg text-center">Total Price: &nbsp; ${{data_getPriceSell.data.price.toFixed(2)}} &nbsp; &nbsp; &nbsp; Unit Price &nbsp; ${{pricePerUnitSell}}</p>
              </div>
              <div v-else>
                <p class="relative text-lg text-center"><br></p>
              </div>




              <p class="relative text-lg text-center">your buy orders</p>

              <DataTable selectionMode="single" v-model:selection="selectedBuyOrderForCancel" :value="currentPersonBuyOrders" size="small" scrollable scrollHeight="190px" tableStyle="min-width: 10rem" >
                <Column field="price" header="Price">
                  <template #body="slotProps">
                    <span>${{ slotProps.data.price.toFixed(2) }}</span>
                  </template>
                </Column>
                <Column field="quantity" header="Quantity"></Column>
                <Column field="quantity_available" header="Quantity Available">
                  <template #body="slotProps">
                    <Tag :value="slotProps.data.quantity_available" :severity="chooseSeverityStatus(slotProps.data.quantity, slotProps.data.quantity_available)" />
                </template>
                </Column>
              </DataTable>

              <div v-if="selectedBuyOrderForCancel" >
                <Button style="width: 100%;" type="submit" severity="info" label="cancel listing" size="small" @click="cancelBuyOrder(selectedBuyOrderForCancel.id)" rounded />
              </div>



            </div>


          </div>

        </div>

      </div>



    </div>


  </div>

  
</template>



<style scoped>


.flexbox-container-top {
  display: flex;
  justify-content: space-around;
  height: 16vh;
  min-height: 130px;
}

.flexbox-container-bottom {
  display: flex;
  justify-content: space-around;
  height: 65vh;
}

.flexbox-container {
  display: flex;
  justify-content: space-around;
  height: 84vh;
}

.flexbox-item-colorless {
  width: 300px;
  margin: 8px;
  background-color: #f0f2f5;
}

.flexbox-item-sub {
  width: 300px;
  border: 3px solid #b4bed4;
  background-color: #ffffff;
  margin: 0px;
  width: 100%;
}

.flexbox-item {
  width: 300px;
  margin: 8px;
  border: 3px solid #b4bed4;
  background-color: #ffffff;
}

.flexbox-item-1 {
  flex-grow: 1;
}

.flexbox-item-2 {
  flex-grow: 1;
}

.flexbox-item-3 {
  flex-grow: 1;
}

.flexbox-item-4 {
  flex-grow: 1;
}

.flexbox-item-5 {
  flex-grow: 1;
}

.flexbox-item-6 {
  flex-grow: 1;
}

.flexbox-item-7 {
  flex-grow: 1;
}

.flexbox-item-8 {
  flex-grow: 1;

  height: 70%;
  min-height: 455px;
}

.flexbox-item-9 {
  flex-grow: 1;

  height: 27.6%;
  min-height: 170px;

  margin-top: 16px;
}



.flexbox-item-10 {
  flex-grow: 1;

  height: 55%;
  min-height: 365px;
}

.flexbox-item-11 {
  flex-grow: 1;

  height: 42.6%;
  min-height: 270px;

  margin-top: 16px;
}




.flexbox-item-12 {
  flex-grow: 1;

  height: 55%;
  min-height: 365px;
}




</style>
