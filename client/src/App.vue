<template>
   <header
      class="sticky z-40 top-0 bg-background/80 backdrop-blur-lg border-b border-border"
   >
      <div class="header-container px-4 py-2 flex items-center">
         <div class="logo mr-2">
            <img
               src="https://www.saokim.com.vn/blog/wp-content/uploads/2022/04/logo-moi-cua-starbucks.jpg.webp"
               alt=""
               class="w-10 aspect-square object-contain"
            />
         </div>

         <NavigationMenu>
            <NavigationMenuList>
               <NavigationMenuItem :class="navigationMenuTriggerStyle()">
                  <RouterLink
                     :to="{
                        name: 'enhancer-view',
                     }"
                  >
                     Enhancer
                  </RouterLink>
               </NavigationMenuItem>
               <NavigationMenuItem
                  :class="navigationMenuTriggerStyle()"
                  @click="console.log($route.path)"
               >
                  <RouterLink
                     :to="{
                        name: 'filters-view',
                     }"
                     >Filters</RouterLink
                  >
               </NavigationMenuItem>
            </NavigationMenuList>
         </NavigationMenu>

         <span class="spacer grow"></span>

         <div class="icon-buttons flex">
            <DropdownMenu>
               <DropdownMenuTrigger asChild>
                  <Button
                     variant="ghost"
                     size="icon"
                  >
                     <Globe class="w-5 h-5" />
                  </Button>
               </DropdownMenuTrigger>

               <DropdownMenuContent
                  class="w-auto pr-10"
                  align="end"
               >
                  <DropdownMenuLabel>Choose language</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuRadioGroup v-model="language">
                     <DropdownMenuRadioItem value="en">
                        English
                     </DropdownMenuRadioItem>
                     <DropdownMenuRadioItem value="vi">
                        Tiếng Việt
                     </DropdownMenuRadioItem>
                  </DropdownMenuRadioGroup>
               </DropdownMenuContent>
            </DropdownMenu>

            <Sheet>
               <SheetTrigger asChild>
                  <Button
                     variant="ghost"
                     size="icon"
                  >
                     <AlignRight class="w-5 h-5" />
                  </Button>
               </SheetTrigger>

               <SheetContent>
                  <SheetHeader>
                     <VisuallyHidden>
                        <SheetTitle></SheetTitle>
                        <SheetDescription></SheetDescription>
                     </VisuallyHidden>

                     <SheetClose>
                        <RouterLink
                           :to="{
                              name: 'enhancer-view',
                           }"
                           class="flex items-center"
                        >
                           <Globe class="w-5 h-5 mr-2" />
                           <span class="font-bold">Enhancer</span>
                        </RouterLink>
                     </SheetClose>
                  </SheetHeader>

                  <div
                     class="menu-items-container overflow-y-auto h-[calc(100vh-8rem)] mt-4"
                  >
                     <div
                        class="menu-items-group text-gray-500 flex flex-col gap-y-1 mb-2"
                        v-for="(group, groupIndex) in MENU_ITEMS"
                     >
                        <p
                           :key="groupIndex"
                           class="menu-items-group-title uppercase font-bold text-xs py-1"
                        >
                           {{ group.title }}
                        </p>

                        <ul>
                           <li
                              class="menu-item flex items-center gap-x-2.5 py-2 cursor-pointer rounded-lg font-medium"
                              v-for="(item, itemIndex) in group.items"
                              :key="itemIndex"
                           >
                              <component
                                 :is="item.icon"
                                 class="h-5"
                              ></component>
                              <p class="text-sm">{{ item.text }}</p>
                           </li>
                        </ul>
                     </div>
                  </div>

                  <div class="flex px-4 py-3 rounded-lg bg-zinc-100">
                     <span class="text-sm">Appearance</span>
                     <span class="spacer grow"></span>
                     <Switch
                        :checked="isDark"
                        @update:checked="isDark = !isDark"
                     >
                        <template #thumb>
                           <span class="w-full h-full grid place-items-center">
                              <Moon
                                 class="w-4 h-4"
                                 v-if="isDark"
                              />
                              <Sun
                                 class="w-4 h-4"
                                 v-else
                              />
                           </span>
                        </template>
                     </Switch>
                  </div>
               </SheetContent>
            </Sheet>
         </div>
      </div>
   </header>

   <main>
      <router-view></router-view>
   </main>
   <footer>This is footer</footer>
</template>

<script setup lang="ts">
   import {
      NavigationMenu,
      NavigationMenuItem,
      NavigationMenuList,
      navigationMenuTriggerStyle,
   } from '@/components/ui/navigation-menu';
   import {
      Sheet,
      SheetContent,
      SheetDescription,
      SheetHeader,
      SheetTitle,
      SheetTrigger,
      SheetClose,
   } from '@/components/ui/sheet';
   import {
      DropdownMenu,
      DropdownMenuContent,
      DropdownMenuLabel,
      DropdownMenuRadioGroup,
      DropdownMenuRadioItem,
      DropdownMenuSeparator,
      DropdownMenuTrigger,
   } from '@/components/ui/dropdown-menu';
   import { Button } from '@/components/ui/button';
   import { Switch } from '@/components/ui/switch';
   import { Globe, AlignRight, Moon, Sun } from 'lucide-vue-next';
   import { MENU_ITEMS } from '@/utils/constants';
   import { ref } from 'vue';
   import { VisuallyHidden } from 'radix-vue';

   const language = ref('en');
   const isDark = ref(false);
</script>

<style scoped>
   * {
      /* border: 1px solid #75757583; */
   }
</style>
